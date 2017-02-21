import uuid
from django.db import models
from django.db.models import Sum, Case, When
from django.contrib.auth import hashers
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

import pinax.stripe.models as pinax_models


class User(AbstractUser):
    name = models.CharField(max_length=255, blank=True, null=True)


class Subscription(pinax_models.Subscription):
    """GreenToGo subscription model.

    A subscription can belong to more than one subscriber.
    One or more subscriptions can belong to the same subscriber.
    This should be a many-to-many relationship.
    """

    class Meta:
        proxy = True

    @property
    def number_of_boxes(self):
        try:
            number_of_boxes = int(
                self.plan.metadata.get("number_of_boxes", "1"))
        except ValueError:
            number_of_boxes = 1

        return number_of_boxes

    def available_boxes(self):
        boxes_checked_out = LocationTag.objects.filter(
            subscription=self).aggregate(checked_out=Sum(
                Case(
                    When(
                        location__service=Location.CHECKOUT, then=1),
                    When(
                        location__service=Location.CHECKIN, then=-1),
                    default=1,
                    output_field=models.IntegerField())))['checked_out']
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
    subscriptions = models.ManyToManyField(
        Subscription, related_name="subscribers")

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
    SERVICE_CHOICES = (
        (CHECKIN, 'Check in'),
        (CHECKOUT, 'Check out'), )

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
