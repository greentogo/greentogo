from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import hashers
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import EmailMessage
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Case, Q, Sum, When
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.text import slugify

import shortuuid
from django_geocoder.wrapper import get_cached as geocode

from core.stripe import stripe
from core.utils import decode_id, encode_nums


class User(AbstractUser):
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(
        verbose_name='Email address',
        max_length=255,
        unique=True,
    )
    stripe_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name or self.username

    def has_active_subscription(self):
        return self.subscriptions.active().count() > 0

    def create_stripe_customer(self, token=None):
        if self.stripe_id is not None:
            return

        if token is None:
            customer = stripe.Customer.create(
                email=self.email,
            )
        else:
            customer = stripe.Customer.create(
                email=self.email,
                source=token,
            )

        self.stripe_id = customer.id
        self.save()
        return customer

    def get_stripe_customer(self, create=False):
        if self.stripe_id is None:
            if create:
                return self.create_stripe_customer()
            else:
                return None

        customer = stripe.Customer.retrieve(self.stripe_id)
        return customer


class CannotChangeException(Exception):
    """Raise when model field should not change after initial creation."""


class PlanQuerySet(models.QuerySet):
    def available(self):
        return self.filter(available=True).exclude(stripe_id=None)

    def as_dicts(self):
        return [plan.as_dict() for plan in self.all()]


class Plan(models.Model):
    objects = PlanQuerySet.as_manager()

    name = models.CharField(max_length=255, unique=True)
    available = models.BooleanField(default=True)
    amount = models.PositiveIntegerField(help_text="Amount in cents.")
    number_of_boxes = models.PositiveIntegerField()
    stripe_id = models.CharField(max_length=255, unique=True, blank=True, null=True, editable=False)

    class Meta:
        ordering = ['amount', 'number_of_boxes']

    @classmethod
    def from_db(cls, db, field_names, values):
        """Overridden in order to allow us to see if a value has changed."""
        instance = super().from_db(db, field_names, values)
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def as_dict(self):
        return {
            'stripe_id': self.stripe_id,
            'name': self.name,
            'amount': self.amount,
            'display_price': self.display_price(),
            'boxes': self.number_of_boxes
        }

    def display_price(self):
        return "${:.02f}".format(self.amount / 100)

    def is_changed(self, field_name):
        """Find out if a value has changed since it was pulled from the DB."""
        old_value = self._loaded_values[field_name]
        new_value = getattr(self, field_name)
        return not old_value == new_value

    def __str__(self):
        return self.name

    def _generate_stripe_id(self, force=False):
        if force or not self.stripe_id:
            shortuuid.set_alphabet("23456789ABCDEFGHJKLMNPQRSTUVWXYZ")
            stripe_id = slugify(self.name) + shortuuid.uuid()[:6]
            while Plan.objects.filter(stripe_id=stripe_id).count() > 0:
                stripe_id = slugify(self.name) + "-" + shortuuid.uuid()[:6]
            return stripe_id

    def save(self, *args, **kwargs):
        if self.stripe_id:
            if self.is_changed('amount'):
                raise CannotChangeException({"model": self, "field": "amount"})
            if self.is_changed('name'):
                stripe_plan = stripe.Plan.retrieve(self.stripe_id)
                stripe_plan.name = self.name
                stripe_plan.save()
        else:
            self.stripe_id = self._generate_stripe_id()
            plan = stripe.Plan.create(
                name=self.name,
                id=self.stripe_id,
                interval="year",
                currency="usd",
                amount=self.amount,
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.available = False
        self.save()


class UnclaimedSubscription(models.Model):
    email = models.EmailField(unique=True)
    plan = models.ForeignKey(Plan)
    claimed = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {}".format(self.email, self.plan)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def claim_subscriptions(sender, instance, created, **kwargs):
    if created:
        unsubs = UnclaimedSubscription.objects.filter(email=instance.email, claimed=False)
        for unsub in unsubs:
            subscription, _ = Subscription.objects.get_or_create(user=instance, plan=unsub.plan)
            unsub.claimed = True
            unsub.save()


@receiver(user_logged_in)
def claim_subscriptions_on_login(sender, user, request, **kwargs):
    unsubs = UnclaimedSubscription.objects.filter(email=user.email, claimed=False)
    for unsub in unsubs:
        subscription, _ = Subscription.objects.get_or_create(user=user, plan=unsub.plan)
        unsub.claimed = True
        unsub.save()


class SubscriptionQuerySet(models.QuerySet):
    def active(self):
        return self.filter(Q(ends_at=None) | Q(ends_at__gt=timezone.now()))

    def owned_by(self, user):
        return self.filter(user=user)


class Subscription(models.Model):
    objects = SubscriptionQuerySet.as_manager()

    name = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, related_name="subscriptions")
    plan = models.ForeignKey(Plan, null=True)
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True)
    stripe_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_status = models.CharField(max_length=100, default="active")

    def __str__(self):
        return "{} - {}".format(self.user.name, self.display_name)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('subscription', kwargs={"sub_id": self.id})

    @classmethod
    def create_from_stripe_sub(cls, user, plan, stripe_subscription):
        subscription = Subscription.objects.create(
            user=user,
            stripe_id=stripe_subscription.id,
            plan=plan,
            ends_at=datetime.fromtimestamp(stripe_subscription.current_period_end) +
            timedelta(days=3),
            stripe_status=stripe_subscription.status
        )
        return subscription

    @classmethod
    def get_from_hashed_id(cls, hashed_id):
        real_id = decode_id(hashed_id)[0]
        return cls.objects.get(id=real_id)

    @property
    def hashed_id(self):
        return encode_nums(self.id)

    @property
    def display_name(self):
        return self.name or self.plan_display()

    def plan_display(self):
        if self.plan:
            return self.plan.name
        return "None"

    def amount_display(self):
        return "${:.2f}".format(self.amount() / 100)

    @property
    def number_of_boxes(self):
        if self.plan:
            return self.plan.number_of_boxes

        return 0

    @property
    def max_boxes(self):
        return self.number_of_boxes

    @property
    def available_boxes(self):
        boxes_checked_out = LocationTag.objects.filter(subscription=self).aggregate(
            checked_out=Sum(
                Case(
                    When(location__service=Location.CHECKOUT, then=1),
                    When(location__service=Location.CHECKIN, then=-1),
                    default=1,
                    output_field=models.IntegerField()
                )
            )
        )['checked_out']
        return self.number_of_boxes - (boxes_checked_out or 0)

    def boxes_checked_out(self):
        return self.number_of_boxes - self.available_boxes

    def amount(self):
        return self.plan.amount

    def can_checkout(self):
        return self.available_boxes > 0

    def can_checkin(self):
        return self.available_boxes < self.number_of_boxes

    def can_tag_location(self, location):
        if location.service == Location.CHECKIN:
            return self.can_checkin()
        else:
            return self.can_checkout()

    def tag_location(self, location):
        tag = LocationTag.objects.create(subscription=self, location=location)
        return tag

    def will_auto_renew(self):
        return self.stripe_id and self.stripe_status == "active"

    def has_stripe_subscription(self):
        return self.stripe_id is not None

    def get_stripe_subscription(self):
        if self.stripe_id is None:
            return None

        return stripe.Subscription.retrieve(self.stripe_id)

    def sync_with_stripe(self, stripe_sub=None):
        if stripe_sub is None:
            stripe_sub = self.get_stripe_subscription()

        if stripe_sub is None:
            return

        self.stripe_id = stripe_sub.id
        self.stripe_status = stripe_sub.status
        if stripe_sub.ended_at:
            self.ends_at = timezone.make_aware(datetime.fromtimestamp(stripe_sub.ended_at))
        else:
            self.ends_at = timezone.make_aware(
                datetime.fromtimestamp(stripe_sub.current_period_end) + timedelta(days=3)
            )
        self.save()


class Location(models.Model):
    CHECKIN = 'IN'
    CHECKOUT = 'OUT'
    SERVICE_CHOICES = ((CHECKIN, 'Check in'), (CHECKOUT, 'Check out'), )

    code = models.CharField(max_length=6, unique=True)
    service = models.CharField(max_length=25, choices=SERVICE_CHOICES)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=1023)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.name, self.service)

    def save(self, *args, **kwargs):
        self._set_code()
        self._geocode()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('location', kwargs={"location_code": self.code})

    def _set_code(self, force=False):
        if force or not self.code:
            shortuuid.set_alphabet("23456789ABCDEFGHJKLMNPQRSTUVWXYZ")
            code = shortuuid.uuid()[:6]
            while Location.objects.filter(code=code).count() > 0:
                code = shortuuid.uuid()[:6]
            self.code = code

    def _geocode(self):
        if self.address and self.latitude is None or self.longitude is None:
            result = geocode(self.address, provider='google')
            if result.latlng:
                lat, lng = result.latlng
                self.latitude = lat
                self.longitude = lng

    def add_qrcode_to_pdf(self, pdf):
        import qrcode
        from reportlab.lib.units import inch

        width, height = pdf._pagesize

        qr = qrcode.QRCode(box_size=10)
        qr.add_data(settings.URL + self.get_absolute_url())
        qr.make(fit=True)
        img = qr.make_image(fill_color="white", back_color="black")

        image_y = 11 * inch - img.pixel_size
        text_y = image_y + 15
        font_size = 14

        pdf.drawInlineImage(img, x=(width - img.pixel_size) / 2, y=image_y)
        pdf.setFont("Helvetica-Bold", font_size)
        pdf.drawCentredString(width / 2, text_y, self.code)
        pdf.setFont("Helvetica", font_size)
        pdf.drawCentredString(
            width / 2, text_y - (font_size + 2), "{} - {}".format(self.name, self.service)
        )
        pdf.showPage()
        return pdf


class LocationTag(models.Model):
    subscription = models.ForeignKey(Subscription)
    location = models.ForeignKey(Location)
    created_at = models.DateTimeField(auto_now_add=True)


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=1023)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    phase = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.address and self.latitude is None or self.longitude is None:
            result = geocode(self.address, provider='google')
            lat, lng = result.latlng
            self.latitude = lat
            self.longitude = lng
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
