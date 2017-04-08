from django.conf import settings
from django.contrib.auth import hashers
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Case, Sum, When
from django.db.models.signals import post_save
from django.dispatch import receiver

import pinax.stripe.models as pinax_models
import shortuuid
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


class User(AbstractUser):
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(
        verbose_name='Email address',
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.name or self.username

    @property
    def subscriptions(self):
        return self.subscriber.subscriptions


class SubscriptionQuerySet(models.QuerySet):
    def active(self):
        return self.filter(pinax_subscription__ended_at=None)

    def owned_by(self, user):
        return self.filter(pinax_subscription__customer=user.customer)

    def reverse_chrono_order(self):
        return self.order_by("-pinax_subscription__current_period_end")


class SubscriptionManager(models.Manager):
    def get_queryset(self):
        return SubscriptionQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()


class Subscription(models.Model):
    """GreenToGo subscription model.

    A subscription can belong to more than one subscriber.
    One or more subscriptions can belong to the same subscriber.
    This should be a many-to-many relationship.
    """
    subscribers = models.ManyToManyField("Subscriber", related_name="subscriptions")
    pinax_subscription = models.OneToOneField(
        pinax_models.Subscription, related_name="g2g_subscription"
    )

    objects = SubscriptionManager()

    @classmethod
    def create_from_pinax_subscription(cls, pinax_subscription):
        sub = cls.objects.create(pinax_subscription=pinax_subscription)
        sub.subscribers.add(pinax_subscription.customer.user.subscriber)
        return sub

    @classmethod
    def lookup_by_customer_and_sub_id(cls, customer, sub_id):
        # TODO handle exceptions
        pinax_sub = customer.subscription_set.get(stripe_id=sub_id)
        try:
            return pinax_sub.g2g_subscription
        except ObjectDoesNotExist:
            return cls.create_from_pinax_subscription(pinax_sub)

    @property
    def customer(self):
        return self.pinax_subscription.customer

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
        try:
            number_of_boxes = int(self.pinax_subscription.plan.metadata.get("number_of_boxes", "1"))
        except ValueError:
            number_of_boxes = 1

        return number_of_boxes

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
        # TODO raise exception if you illegally tag
        return self.locationtag_set.create(location=location)

    def cancel(self):
        subscriptions.cancel(self.pinax_subscription, at_period_end=False)


class Subscriber(models.Model):
    """GreenToGo subscriber model.

    A subscriber can have one or more subscriptions.
    A subscriber belongs to a user.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @property
    def username(self):
        return self.user.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_subscriber(sender, instance, created, **kwargs):
    if created:
        Subscriber.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_stripe_customer(sender, instance, created, **kwargs):
    if created:
        from pinax.stripe.actions import customers
        customers.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_subscriber(sender, instance, **kwargs):
    instance.subscriber.save()


@receiver(post_save, sender=pinax_models.Subscription)
def create_g2g_subscription(sender, instance, created, **kwargs):
    if created:
        Subscription.create_from_pinax_subscription(instance)


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
