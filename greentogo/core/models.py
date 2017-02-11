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


class User(AbstractUser):
    pass


class Subscriber(models.Model):
    """GreenToGo subscriber model.

    A subscriber can have one or more subscriptions.
    A subscriber belongs to a user.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscriptions = models.ManyToManyField('Subscription')

    @property
    def username(self):
        return self.user.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_subscriber(sender, instance, created, **kwargs):
    if created:
        Subscriber.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_subscriber(sender, instance, **kwargs):
    instance.subscriber.save()


class Subscription(models.Model):
    """GreenToGo subscription model.

    A subscription can belong to more than one subscriber.
    One or more subscriptions can belong to the same subscriber.
    This should be a many-to-many relationship.
    """
    admin = models.ForeignKey(Subscriber, related_name="owned_subscriptions")
    plan = models.ForeignKey('SubscriptionPlan')
    started_on = models.DateField()
    expires_on = models.DateField(blank=True, null=True)
    stripe_id = models.CharField(
        max_length=100, unique=True, blank=True, null=True)

    def __str__(self):
        return "{}: {}".format(self.admin, self.plan)

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
        return self.plan.number_of_boxes - (boxes_checked_out or 0)

    def can_checkout(self):
        return self.available_boxes() > 0

    def tag_location(self, location):
        self.locationtag_set.create(location=location)


class SubscriptionPlan(models.Model):
    code = models.CharField(
        max_length=25,
        unique=True,
        help_text="Code must be capital letters and numbers with no spaces.",
        validators=[RegexValidator(r"^[A-Z0-9]+$"), ])
    description = models.CharField(max_length=255)
    number_of_boxes = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.description


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
