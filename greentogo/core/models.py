import uuid
from django.db import models
from django.db.models import Sum, Case, When
from django.contrib.auth import hashers
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class Customer(models.Model):
    """GreenToGo customer model.

    A customer can have one or more subscriptions.
    A customer can have one or more emails.
    """
    name = models.CharField(max_length=255)
    subscriptions = models.ManyToManyField('Subscription')
    _encrypted_password = models.CharField(max_length=100)

    @property
    def password(self):
        if not hasattr(self, '_password'):
            self._password = None
        return self._password

    @password.setter
    def password(self, password):
        self.set_password(password)

    @password.deleter
    def password(self):
        self._password = None

    def set_password(self, password):
        self._password = password
        self._encrypted_password = hashers.make_password(password)

    def check_password(self, possible_password):
        return hashers.check_password(
            password=possible_password,
            encoded=self._encrypted_password,
            setter=self.set_password)


class EmailAddress(models.Model):
    customer = models.ForeignKey(Customer)
    address = models.EmailField()


class Subscription(models.Model):
    """GreenToGo subscription model.

    A subscription can belong to more than one customer.
    One or more subscriptions can belong to the same customer.
    This should be a many-to-many relationship.
    """
    admin = models.ForeignKey(Customer)
    plan = models.ForeignKey('SubscriptionPlan')
    started_on = models.DateTimeField()
    expires_on = models.DateTimeField(blank=True, null=True)
    stripe_id = models.CharField(
        max_length=100, unique=True, blank=True, null=True)

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
        validators=[RegexValidator(r"^[A-Z0-9]$"), ])
    description = models.CharField(max_length=255)
    number_of_boxes = models.PositiveIntegerField(null=True, blank=True)


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
