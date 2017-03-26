import uuid

from django.conf import settings
from django.contrib.auth import hashers
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Case, Sum, When
from django.db.models.signals import post_save
from django.dispatch import receiver

import pinax.stripe.models as pinax_models
from django_geocoder.wrapper import get_cached as geocode


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


# TODO Change from inheritance to composition
class Subscription(pinax_models.Subscription):
    """GreenToGo subscription model.

    A subscription can belong to more than one subscriber.
    One or more subscriptions can belong to the same subscriber.
    This should be a many-to-many relationship.
    """

    class Meta:
        proxy = True

    @classmethod
    def lookup_by_customer_and_sub_id(cls, customer, sub_id):
        # TODO handle exceptions
        subscription = customer.subscription_set.get(stripe_id=sub_id)
        return cls.from_pinax(subscription)

    @classmethod
    def from_pinax(cls, sub):
        return cls.objects.get(pk=sub.pk)

    @property
    def canceled(self):
        return self.canceled_at is not None

    @property
    def number_of_boxes(self):
        try:
            number_of_boxes = int(self.plan.metadata.get("number_of_boxes", "1"))
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

    def tag_location(self, location):
        return self.locationtag_set.create(location=location)


class Subscriber(models.Model):
    """GreenToGo subscriber model.

    A subscriber can have one or more subscriptions.
    A subscriber belongs to a user.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscriptions = models.ManyToManyField(Subscription, related_name="subscribers")

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


class Location(models.Model):
    CHECKIN = 'IN'
    CHECKOUT = 'OUT'
    SERVICE_CHOICES = ((CHECKIN, 'Check in'), (CHECKOUT, 'Check out'), )

    uuid = models.UUIDField(primary_key=True)
    service = models.CharField(max_length=25, choices=SERVICE_CHOICES)

    def save(self, *args, **kwargs):
        if self.uuid is None:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)


class LocationTag(models.Model):
    subscription = models.ForeignKey(Subscription)
    location = models.ForeignKey(Location)
    created_at = models.DateTimeField(auto_now_add=True)


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=1023)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.address and self.latitude is None or self.longitude is None:
            result = geocode(self.address, provider='google')
            lat, lng = result.latlng
            self.latitude = lat
            self.longitude = lng
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
