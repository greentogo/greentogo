import pinax.stripe.models as pinax_models
import shortuuid
from django.conf import settings
from django.contrib.auth import hashers
from django.contrib.auth.models import AbstractUser
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import EmailMessage
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Case, Sum, When
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django_geocoder.wrapper import get_cached as geocode
from pinax.stripe.actions import subscriptions


def get_plan_price(plan):
    return "${:.02f}".format(plan.amount)


def plan_to_dict(plan):
    return {
        'stripe_id': plan.stripe_id,
        'name': plan.name,
        'amount': int(plan.amount * 100),
        'display_price': get_plan_price(plan)
    }


def get_plans():
    plans = pinax_models.Plan.objects.order_by('amount')
    return [plan_to_dict(plan) for plan in plans]


def max_boxes_for_subscription(pinax_sub):
    try:
        number_of_boxes = int(pinax_sub.plan.metadata.get("number_of_boxes", "1"))
    except ValueError:
        number_of_boxes = 1
    return number_of_boxes


def available_boxes_for_subscription(pinax_sub):
    boxes_checked_out = LocationTag.objects \
        .filter(subscription=pinax_sub) \
        .aggregate(
        checked_out=Sum(
            Case(
                When(location__service=Location.CHECKOUT, then=1),
                When(location__service=Location.CHECKIN, then=-1),
                default=1,
                output_field=models.IntegerField()
            )
        )
    )['checked_out']
    return max_boxes_for_subscription(pinax_sub) - (boxes_checked_out or 0)


class User(AbstractUser):
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(
        verbose_name='Email address',
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.name or self.username


class SubscriptionInvitation(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=40)
    pinax_subscription = models.ForeignKey(pinax_models.Subscription, related_name="invitations")

    def save(self, *args, **kwargs):
        if not self.code:
            shortuuid.set_alphabet("23456789ABCDEFGHJKLMNPQRSTUVWXYZ")
            self.code = shortuuid.uuid()
        return super().save(*args, **kwargs)

    def accept(self, user):
        subscription, created = Subscription.objects.get_or_create(
            user=user, pinax_subscription=self.pinax_subscription
        )
        self.delete()
        return subscription

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('invitation', kwargs={"invitation_code": self.code})

    def send_invitation(self):
        site = Site.objects.get_current()
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "https")
        ctx = {
            "owner": self.pinax_subscription.customer.user,
            "invitation": self,
            "site": site,
            "protocol": protocol,
        }
        subject = "Invitation to share a GreenToGo subscription"
        message = render_to_string("email/invitation.txt", ctx)

        EmailMessage(
            subject, message, to=[self.email], from_email=settings.DEFAULT_FROM_EMAIL
        ).send()


class SubscriptionQuerySet(models.QuerySet):
    def active(self):
        return self.filter(pinax_subscription__ended_at=None)

    def owned_by(self, user):
        return self.filter(pinax_subscription__customer=user.customer)

    def reverse_chrono_order(self):
        return self.order_by("-pinax_subscription__current_period_end")


class Subscription(models.Model):
    """GreenToGo subscription model.

    Connects users to subscription objects in Stripe.
    """
    objects = SubscriptionQuerySet.as_manager()

    name = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, related_name="subscriptions")
    pinax_subscription = models.ForeignKey(
        pinax_models.Subscription, related_name="user_subscriptions"
    )

    class Meta:
        unique_together = (('user', 'pinax_subscription', ), )

    @classmethod
    def create_for_subscription_owner(cls, pinax_subscription):
        return cls.objects.create(
            pinax_subscription=pinax_subscription, user=pinax_subscription.customer.user
        )

    @classmethod
    def lookup_by_customer_and_sub_id(cls, customer, sub_id):
        # TODO handle exceptions
        pinax_sub = customer.subscription_set.get(stripe_id=sub_id)
        try:
            return pinax_sub.user_subscriptions.get(user=customer.user)
        except ObjectDoesNotExist:
            return cls.create_for_subscription_owner(pinax_sub)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('subscription', kwargs={"sub_id": self.stripe_id})

    @property
    def customer(self):
        return self.pinax_subscription.customer

    @property
    def owner(self):
        return self.customer.user

    def is_owner_subscription(self):
        return self.user == self.owner

    @property
    def other_subscriptions(self):
        return self.pinax_subscription.user_subscriptions.exclude(user=self.user)

    @property
    def display_name(self):
        return self.name or self.plan_display()

    def plan_display(self):
        return self.pinax_subscription.plan_display()

    @property
    def stripe_id(self):
        return self.pinax_subscription.stripe_id

    @property
    def canceled(self):
        return self.pinax_subscription.canceled_at is not None

    @property
    def total_amount(self):
        return self.pinax_subscription.total_amount

    @property
    def current_period_end(self):
        return self.pinax_subscription.current_period_end

    @property
    def auto_renew(self):
        return not self.pinax_subscription.cancel_at_period_end

    @property
    def number_of_boxes(self):
        return max_boxes_for_subscription(self.pinax_subscription)

    def available_boxes(self):
        return available_boxes_for_subscription(self.pinax_subscription)

    def can_checkout(self):
        return self.available_boxes() > 0

    def can_checkin(self):
        return self.available_boxes() < self.number_of_boxes

    def can_tag_location(self, location):
        if location.service == Location.CHECKIN:
            return self.can_checkin()
        else:
            return self.can_checkout()

    def tag_location(self, location):
        tag = LocationTag.objects.create(subscription=self.pinax_subscription, location=location)
        # TODO raise exception if you illegally tag
        return tag

    def cancel(self):
        subscriptions.cancel(self.pinax_subscription, at_period_end=False)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_stripe_customer(sender, instance, created, **kwargs):
    if created:
        from pinax.stripe.actions import customers
        customers.create(user=instance)


@receiver(post_save, sender=pinax_models.Subscription)
def create_g2g_subscription(sender, instance, created, **kwargs):
    if created:
        Subscription.create_for_subscription_owner(instance)


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


class LocationTag(models.Model):
    subscription = models.ForeignKey(pinax_models.Subscription)
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
