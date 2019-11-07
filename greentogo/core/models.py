import re, rollbar, shortuuid, logging, sys

from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib.auth import hashers
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in
from django.contrib.sites.models import Site
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Case, Count, Q, Sum, When
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.text import slugify
from django.core.mail import send_mail, EmailMessage
from django.db.models.functions import Length
from collections import Counter
from exponent_server_sdk import PushClient, PushMessage, PushResponseError, PushServerError, DeviceNotRegisteredError
from requests.exceptions import ConnectionError, HTTPError

from django_geocoder.wrapper import get_cached as geocode
from postgres_stats import DateTrunc
from templated_email import send_templated_mail

from core.stripe import stripe
from core.utils import decode_id, encode_nums


logger = logging.getLogger('django')

# Types for LocationTag and GroupOrder
CUP = 'CUP'
BOX = 'BOX'
ITEM_CHOICES = (
    (CUP, 'Cup'),
    (BOX, 'Box'),
)

def one_year_from_now():
    return timezone.now() + timedelta(days=365)


def activity_data(days=30):
    begin_datetime = timezone.now() - timedelta(days=days)
    begin_datetime_start_of_day = begin_datetime.replace(hour=0, minute=0, second=0)

    def _get_data(qs):
        data = qs.filter(created_at__gte=begin_datetime_start_of_day) \
                 .annotate(date=DateTrunc('created_at', precision='day')) \
                 .values("date") \
                 .annotate(volume=Count("date")) \
                 .order_by("date")
        data = [{"date": d['date'].date(), "volume": d['volume']} for d in data]
        return data

    def _get_user_data():
        # TODO filter this to only count active subscriptions
        # TODO filter this to only count active subscriptions
        # TODO filter this to only count active subscriptions
        # TODO filter this to only count active subscriptions
        # TODO filter this to only count active subscriptions
        # TODO filter this to only count active subscriptions
        total_active_subs = Subscription.objects.all().count()

        data = LocationTag.objects.filter(created_at__gte=begin_datetime_start_of_day) \
                .annotate(date=DateTrunc('created_at', precision='day')) \
                .values("date", "subscription") \
                .distinct() \
                .order_by("date")

        data = dict(Counter(d['date'].date() for d in data))
        data = [{"date": date, "volume": "{0:.2f}".format(subs/total_active_subs * 100.0)} for date, subs in data.items()]
        return data

    checkin_data = _get_data(LocationTag.objects.checkin())
    checkout_data = _get_data(LocationTag.objects.checkout())

    user_percentage_data = _get_user_data()
    return {"checkin": checkin_data, "checkout": checkout_data, "user": user_percentage_data}

def total_boxes_returned():
    return LocationTag.objects.checkin().count()


# Basic arguments. You should extend this function with the push features you
# want to use, or simply pass in a `PushMessage` object.
def send_push_message(token, title, message, extra=None):
    try:
        # TODO look into what ttl is
        # TODO look into channel_id issues on android
        # TODO handle responeses to check if notification was deleivered
        response = PushClient().publish(
            PushMessage(to=token,
                        title=title,
                        body=message,
                        data=extra,
                        sound='default',
                        priority='high'))
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': message,
                'extra': extra,
                'errors': exc.errors,
                'response_data': exc.response_data,
            })
        raise
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        return rollbar.report_exc_info(
            extra_data={'token': token, 'message': message, 'extra': extra})

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
    except DeviceNotRegisteredError:
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': 'INACTIVE TOKEN',
                'extra': extra,
                'errors': exc.errors,
                'response_data': exc.response_data,
            })
        # Mark the push token as inactive
        # from notifications.models import PushToken
        # PushToken.objects.filter(token=token).update(active=False)
    except PushResponseError as exc:
        # Encountered some other per-notification error.
        return rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': message,
                'extra': extra,
                'push_response': exc.push_response._asdict(),
            })

def export_chart_data(start_date=False, end_date=False):
    begin_datetime_start_of_day = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d'), datetime.min.time())
    end_datetime_start_of_day = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d'), datetime.min.time())

    def _get_data(qs):
        data = qs.filter(created_at__gte=begin_datetime_start_of_day, created_at__lte=end_datetime_start_of_day) \
                 .annotate(date=DateTrunc('created_at', precision='day')) \
                 .values("date") \
                 .annotate(volume=Count("date")) \
                 .order_by("date")
        data = [{"date": d['date'].date(), "volume": d['volume']} for d in data]
        return data

    def _get_user_data():
        # filter this to only count active subscriptions
        total_active_subs = Subscription.objects.all().count()

        data = LocationTag.objects.filter(created_at__gte=begin_datetime_start_of_day, created_at__lte=end_datetime_start_of_day) \
                .annotate(date=DateTrunc('created_at', precision='day')) \
                .values("date", "subscription") \
                .distinct() \
                .order_by("date")

        data = dict(Counter(d['date'].date() for d in data))
        data = [{"date": date, "volume": "{0:.2f}".format(subs/total_active_subs * 100.0)} for date, subs in data.items()]
        return data

    checkin_data = _get_data(LocationTag.objects.checkin())
    checkout_data = _get_data(LocationTag.objects.checkout())

    user_percentage_data = _get_user_data()
    return {"checkin": checkin_data, "checkout": checkout_data, "user": user_percentage_data}

class AdminSettings(models.Model):
    lowStockEmails = models.TextField(
            max_length=1024,
            blank=False,
            help_text="List of emails separated by commas for who should recieve alerts when stock is low at restaurants")

    highStockEmails = models.TextField(
            max_length=1024,
            blank=False,
            help_text="List of emails separated by commas for who should recieve alerts when stock is high at return stations")

    newSubEmails = models.TextField(
            max_length=1024,
            blank=False,
            default="info@dontwastedurham.com",
            help_text="List of emails separated by commas for who should recieve alerts about new subscriptions")

    appVideo = models.FileField(upload_to='video/', blank=True, null=True)

    def get_restaurant_low_stock_emails_list(self):
        return re.sub(",", " ",  self.lowStockEmails).split()

    def get_return_high_stock_emails_list(self):
        return re.sub(",", " ",  self.highStockEmails).split()

    def get_new_subscription_emails(self):
        return re.sub(",", " ",  self.newSubEmails).split()

    def save(self, *args, **kwargs):
        if AdminSettings.objects.exists() and not self.pk:
            raise ValidationError('There is can be only one AdminSettings instance')
        return super(AdminSettings, self).save(*args, **kwargs)

class User(AbstractUser):
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(
        verbose_name='Email address',
        max_length=255,
        unique=True,
    )
    referred_by = models.CharField(max_length=255, blank=True, null=True)
    stripe_id = models.CharField(max_length=100, blank=True, null=True)
    expoPushToken = models.CharField(max_length=255, blank=True, null=True)
    restaurant_manager = models.ManyToManyField('Location')

    def __str__(self):
        return self.name or self.username

    def has_active_subscription(self):
        return self.subscriptions.active().count() > 0

    def get_subscriptions(self):
        return self.subscriptions.active().order_by("starts_at")

    def is_corporate_user(self):
        return self.subscriptions.active().is_corporate().count() > 0

    def create_stripe_customer(self, token=None):
        if self.stripe_id:
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
        if not self.stripe_id:
            if create:
                return self.create_stripe_customer()
            else:
                return None

        customer = stripe.Customer.retrieve(self.stripe_id)
        return customer

    def get_all_subids(self):
        return self.subscriptions.all().values_list('pk', flat=True)

    def total_reward_points(self):
        return LocationTag.objects.filter(subscription_id__in=self.get_all_subids(), location__service='IN').annotate(date=DateTrunc('created_at', precision='month')).values('date').distinct().count()

    @property
    def reward_points(self):
        redeemedPoints = Reward.objects.filter(user=self).count() * 6
        return self.total_reward_points() - redeemedPoints

    def total_boxes_checkedin(self):
        return LocationTag.objects.filter(subscription_id__in=self.get_all_subids(), location__service='IN').count()

    def total_boxes_checkedout(self):
        return LocationTag.objects.filter(subscription_id__in=self.get_all_subids(), location__service='OUT').count()


class CannotChangeException(Exception):
    """Raise when model field should not change after initial creation."""

class IncorrectIntervalException(Exception):
    """Raise when the interval string is not the correct type."""

class MobileAppRatings(models.Model):
    user = models.ForeignKey(User)
    rating = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)
    version = models.CharField(max_length=255)

class PlanQuerySet(models.QuerySet):
    def available(self):
        return self.filter(available=True).exclude(stripe_id=None)

    def as_dicts(self):
        return [plan.as_dict() for plan in self.all()]


class Plan(models.Model):
    objects = PlanQuerySet.as_manager()
    INTERVAL_CHOICES = (('month', 'month'), ('year', 'year'), )

    name = models.CharField(max_length=255, unique=True)
    available = models.BooleanField(default=True)
    amount = models.PositiveIntegerField(help_text="Amount in cents.")
    number_of_boxes = models.PositiveIntegerField()
    interval = models.CharField(max_length=255, choices=INTERVAL_CHOICES, help_text="Should say 'year' or 'month'.", default="year")
    stripe_id = models.CharField(max_length=255, unique=True, blank=True, null=True, editable=False)

    class Meta:
        ordering = ['amount', 'number_of_boxes']

    @classmethod
    def from_db(cls, db, field_names, values):
        """Overridden in order to allow us to see if a value has changed."""
        instance = super().from_db(db, field_names, values)
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def g_available(self):
        if self.available:
            return ""
        else:
            return "(UNAVAILABLE)"

    def __str__(self):
        return "{}, Stripe ID: {} {}".format(self.name, self.stripe_id, self.g_available())

    def as_dict(self):
        return {
            'stripe_id': self.stripe_id,
            'name': self.name,
            'amount': self.amount,
            'interval': self.interval,
            'display_price': self.display_price(),
            'boxes': self.number_of_boxes
        }

    def display_price(self, corporate_code=None, coupon_code=None):
        """apply corporate/coupon code and return formatted price"""
        amount = self.amount
        if corporate_code:
            amount -= (corporate_code.amount_off * 100)
        elif coupon_code:
            if coupon_code.is_percentage:
                amount = amount * ((100 - coupon_code.value)/100)
            else:
                amount = amount - (coupon_code.value * 100)
        return "${:.02f}".format(amount / 100)

    def is_changed(self, field_name):
        """Find out if a value has changed since it was pulled from the DB."""
        if not hasattr(self, '_loaded_values'):
            return False
        old_value = self._loaded_values[field_name]
        new_value = getattr(self, field_name)
        return not old_value == new_value

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
            if self.is_changed('interval'):
                raise CannotChangeException({"model": self, "field": "interval"})
            if self.is_changed('name'):
                stripe_plan = stripe.Plan.retrieve(self.stripe_id)
                stripe_plan.name = self.name
                stripe_plan.save()
        else:
            if self.interval == 'year' or self.interval == 'month':
                self.stripe_id = self._generate_stripe_id()
                plan = stripe.Plan.create(
                    name=self.name,
                    id=self.stripe_id,
                    interval=self.interval,
                    currency="usd",
                    amount=self.amount,
                )
            else:
                raise IncorrectIntervalException({"model": self, "field": "interval"})
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.available = False
        self.save()


class UnclaimedSubscription(models.Model):
    email = models.EmailField()
    plan = models.ForeignKey(Plan)
    claimed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('email', 'plan', )

    def __str__(self):
        return "{} - {}".format(self.email, self.plan)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def claim_subscriptions(sender, instance, created, **kwargs):
    if created:
        unsubs = UnclaimedSubscription.objects.filter(email__iexact=instance.email, claimed=False)
        for unsub in unsubs:
            subscription, _ = Subscription.objects.get_or_create(
                user=instance, plan=unsub.plan, defaults={"ends_at": one_year_from_now()}
            )
            unsub.claimed = True
            unsub.save()


@receiver(user_logged_in)
def claim_subscriptions_on_login(sender, user, request, **kwargs):
    unsubs = UnclaimedSubscription.objects.filter(email__iexact=user.email, claimed=False)
    for unsub in unsubs:
        subscription, _ = Subscription.objects.get_or_create(
            user=user, plan=unsub.plan, defaults={"ends_at": one_year_from_now()}
        )
        unsub.claimed = True
        unsub.save()


class SubscriptionQuerySet(models.QuerySet):
    def active(self):
        return self.filter(Q(ends_at=None) | Q(ends_at__gt=timezone.now()))

    def owned_by(self, user):
        return self.filter(user=user)
    
    def is_paying(self):
        return self.annotate(stripe_id_len=Length('stripe_id')).filter(stripe_id_len__gt=3)

    def is_corporate(self):
        return self.filter(corporate_code__isnull=False)

class Subscription(models.Model):
    objects = SubscriptionQuerySet.as_manager()

    name = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, related_name="subscriptions")
    plan = models.ForeignKey(Plan, null=True, blank=True)
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True)
    stripe_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_status = models.CharField(max_length=100, default="active")
    corporate_code = models.ForeignKey('CorporateCode', null=True, blank=True)
    coupon_code = models.ForeignKey('CouponCode', null=True, blank=True)
    cancelled = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {}".format(self.user.username, self.display_name)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('subscription', kwargs={"sub_id": self.id})

    @classmethod
    def create_from_stripe_sub(cls, user, plan, stripe_subscription, corporate_code=None, coupon_code=None):
        ends_at = datetime.fromtimestamp(stripe_subscription.current_period_end) + timedelta(days=3)
        ends_at = timezone.make_aware(ends_at, is_dst=False)
        sub_kwargs = dict(
            user=user,
            stripe_id=stripe_subscription.id,
            plan=plan,
            ends_at=ends_at,
            stripe_status=stripe_subscription.status,
        )

        if corporate_code:
            sub_kwargs['corporate_code'] = corporate_code
        elif coupon_code:
            sub_kwargs['coupon_code'] = coupon_code

        subscription = Subscription.objects.create(**sub_kwargs)
        return subscription

    @classmethod
    def get_from_hashed_id(cls, hashed_id):
        real_id = decode_id(hashed_id)[0]
        return cls.objects.get(id=real_id)

    @property
    def hashed_id(self):
        return encode_nums(self.id)

    @property
    def is_active(self):
        if self.ends_at is not None:
            return self.ends_at.date() > timezone.now().date()
        else:
            return True

    @property
    def display_name(self):
        return self.name or self.plan_display()

    def plan_display(self):
        if self.plan:
            return "Subscription for " + self.plan.name
        return "None"

    def amount_display(self):
        if self.plan:
            return self.plan.display_price(
                    corporate_code=self.corporate_code,
                    coupon_code=self.coupon_code)

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
        return self.number_of_boxes - (self.boxes_currently_out or 0)

    @property
    def boxes_currently_out(self):
        checked_out = LocationTag.objects.filter(subscription=self).aggregate(
                checked_out=Sum(
                    Case(
                        When(location__service=Location.CHECKOUT, then=1),
                        When(location__service=Location.CHECKIN, then=-1),
                        default=1,
                        output_field=models.IntegerField()
                        )
                    )
                )['checked_out'] or 0
        if checked_out < 0:
            logger.warn("User {} has is reporting more boxes available than the"
                        "maximum".format(self.user))
        return checked_out

    def amount(self):
        return self.plan.amount

    def one_year_from_start(self):
        return self.starts_at + timedelta(days=365)

    def can_checkout(self, number_of_boxes=1):
        return self.available_boxes >= number_of_boxes

    def can_checkin(self, number_of_boxes=1):
        return self.available_boxes + number_of_boxes <= self.number_of_boxes

    def can_tag_location(self, location, number_of_boxes=1):
        if location.service == Location.CHECKIN:
            return self.can_checkin(number_of_boxes)
        else:
            return self.can_checkout(number_of_boxes)

    def tag_location(self, location, number_of_boxes=1, user=False):
        tags = []
        for _ in range(number_of_boxes):
            tags.append(LocationTag.objects.create(subscription=self, location=location))
        try:
            if location.notify and len(location.notifyEmail) > 1:
                userEmail = 'N/A'
                userName = 'N/A'
                if user:
                    userEmail = user.email
                    userName = user.name
                message_data = {
                    'email': userEmail,
                    'name': userName,
                    'number_of_boxes': number_of_boxes,
                    'action': location.service
                }
                EmailMessage(
                    subject='GreenToGo Box Notification',
                    body=render_to_string('admin/notify_email.txt', message_data),
                    from_email='greentogo@app.durhamgreentogo.com',
                    to=[location.notifyEmail],
                    reply_to=["amy@durhamgreentogo.com"]
                ).send()

            if not location.admin_location and AdminSettings.objects.first() is not None:
                error_avg_difference = 0
                try:
                    error_avg_difference = int(location.error_avg_difference)
                except Exception:
                    error_avg_difference = 0
                message_data = {
                    'location': location,
                    'count': location.get_estimated_stock(),
                    'errorText': location.error_rate,
                    'badNumber': location.get_estimated_stock() - error_avg_difference,
                }
                if location.service == "OUT":
                    if location.get_estimated_stock() < 7:
                        EmailMessage(
                            subject='Low Stock At {}'.format(location.name),
                            body=render_to_string('admin/low_stock.txt', message_data),
                            from_email='database@app.durhamgreentogo.com',
                            to=AdminSettings.objects.first().get_restaurant_low_stock_emails_list(),
                        ).send()
                    elif location.error_percentage and (location.get_estimated_stock() - error_avg_difference) < 7:
                        EmailMessage(
                            subject='Possible Low Stock At {}'.format(location.name),
                            body=render_to_string('admin/low_stock_possible.txt', message_data),
                            from_email='database@app.durhamgreentogo.com',
                            to=AdminSettings.objects.first().get_restaurant_low_stock_emails_list(),
                        ).send()

                if location.service == "IN" and location.get_estimated_stock() > 6:
                    EmailMessage(
                        subject='Please Empty {}'.format(location.name),
                        body=render_to_string('admin/high_stock.txt', message_data),
                        from_email='database@app.durhamgreentogo.com',
                        to=AdminSettings.objects.first().get_return_high_stock_emails_list(),
                    ).send()

        except Exception as ex:
            rollbar.report_exc_info(sys.exc_info(), ex)
        return tags

    def used_today(self):
        return self.used_on_date(date.today())

    def used_on_date(self, date):
        tag_count = LocationTag.objects.filter(subscription=self, created_at__date=date).count()
        return tag_count > 0

    def last_used(self):
        return LocationTag.objects.filter(subscription_id=self.id).latest('created_at').created_at

    def total_checkins(self):
        return LocationTag.objects.filter(subscription_id=self.id, location__service="IN").count()

    def total_checkouts(self):
        return LocationTag.objects.filter(subscription_id=self.id, location__service="OUT").count()

    def will_auto_renew(self):
        return self.has_stripe_subscription() and self.is_stripe_active() and not self.cancelled

    def is_stripe_active(self):
        return self.stripe_status in ("active", "trialing", )

    def has_stripe_subscription(self):
        return self.stripe_id

    def get_stripe_subscription(self):
        if not self.stripe_id:
            return None

        return stripe.Subscription.retrieve(self.stripe_id)

    def sync_with_stripe(self, stripe_sub=None):
        if stripe_sub is None:
            stripe_sub = self.get_stripe_subscription()

        if stripe_sub is None:
            return

        if stripe_sub.cancel_at_period_end and not self.cancelled:
            self.cancelled = True
        elif not stripe_sub.cancel_at_period_end and self.cancelled:
            self.cancelled = False

        self.stripe_id = stripe_sub.id
        self.stripe_status = stripe_sub.status
        if stripe_sub.ended_at:
            self.ends_at = timezone.make_aware(datetime.fromtimestamp(stripe_sub.ended_at))
        else:
            self.ends_at = timezone.make_aware(
                datetime.fromtimestamp(stripe_sub.current_period_end) + timedelta(days=3)
            )
        self.save()

    def update_stripe(self):
        stripe_sub = self.get_stripe_subscription()

        if stripe_sub is None:
            return

        if self.cancelled and not stripe_sub.cancel_at_period_end:
            if not stripe_sub.status == 'cancelled' or not stripe_sub.status == 'canceled':
                stripe_sub.delete(at_period_end = True)
        elif not self.cancelled and stripe_sub.cancel_at_period_end:
            stripe_sub.modify(
                stripe_sub.id,
                metadata={'cancel_at_period_end': 'false'}
            )

        self.stripe_id = stripe_sub.id
        self.stripe_status = stripe_sub.status
        if stripe_sub.ended_at:
            self.ends_at = timezone.make_aware(datetime.fromtimestamp(stripe_sub.ended_at))
        else:
            self.ends_at = timezone.make_aware(
                datetime.fromtimestamp(stripe_sub.current_period_end) + timedelta(days=3)
            )

    def save(self, *args, **kwargs):
        self.update_stripe()
        super().save(*args, **kwargs)


class SubscriptionUpdateException(Exception):
    def __init__(self, subscription, stripe_subscription, message):
        self.subscription = subscription
        self.stripe_subscription = stripe_subscription
        self.message = message


@receiver(post_save, sender=Subscription)
def new_subscription_email_to_admins(sender, instance, created, **kwargs):
    if created:
        send_templated_mail(
            template_name='new_subscription',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=AdminSettings.objects.first().get_new_subscription_emails(),
            context={'subscription': instance}
        )


class Neighborhood(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return "{}".format(self.name)


class LocationQuerySet(models.QuerySet):
    def checkin(self):
        return self.filter(service=Location.CHECKIN).order_by('name')

    def checkout(self):
        return self.filter(service=Location.CHECKOUT).order_by('name')
    
    def notRetiredOrAdmin(self):
        return self.filter(retired=False, admin_location=False).exclude(name='Apple Testing Location - OUT')

    def dumping_in(self):
        return self.filter(dumping_location=true, service='IN')

    def dumping_out(self):
        return self.filter(dumping_location=true, service='OUT')

    def getTopUsedLocation(self, month, year):
        location = LocationTag.objects.filter(
            location__service=Location.CHECKOUT,
            created_at__year=year,
            created_at__month=month,
        ).values('location').annotate(c=Count('location')).order_by('-c').first()
        if location is not None:
            return self.get(id=location.get('location'))
        else:
            return None


class Location(models.Model):
    objects = LocationQuerySet.as_manager()

    CHECKIN = 'IN'
    CHECKOUT = 'OUT'
    SERVICE_CHOICES = ((CHECKIN, 'Check in'), (CHECKOUT, 'Check out'), )
    TIME_CHOICES = (
        ('Anytime', 'Anytime'),
        ('8am', '8 am'),
        ('9am', '9 am'),
        ('10am', '10 am'),
        ('11am', '11 am'),
        ('12pm', '12 pm'),
        ('1pm', '1 pm'),
        ('2pm', '2 pm'),
        ('3pm', '3 pm'),
        ('4pm', '4 pm'),
        ('5pm', '5 pm'),
        ('6pm', '6 pm'),
        ('7pm', '7 pm'),
        ('8pm', '8 pm'),
        ('9pm', '9 pm'),
    )

    restaurant_manager = models.ManyToManyField(User)
    code = models.CharField(max_length=6, unique=True)
    service = models.CharField(max_length=25, choices=SERVICE_CHOICES)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=1023)
    website = models.CharField(max_length=1023, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    phase = models.PositiveIntegerField(default=1)
    neighborhood = models.ForeignKey(Neighborhood, blank=True, null=True)
    preferred_delivery_time = models.CharField(max_length=25, choices=TIME_CHOICES, default=TIME_CHOICES[0][0])
    has_boxes = models.BooleanField(default=True, help_text="If the location uses take out containers or not")
    has_cups = models.BooleanField(default=False, help_text="If the location uses take out cups or not")
    maximum_boxes = models.IntegerField(default=40)
    minimum_boxes = models.IntegerField(
        default=15,
        help_text="Minimum number of boxes to be kept at this check out \
        location (please ignore for non-check out locations)")

    notify = models.BooleanField(
        default=False,
        help_text="If checked, an email will be sent any \
        time a box is checked in or out of this location")

    notifyEmail = models.CharField(
        blank=True,
        max_length=255,
        help_text="Email for notify option")

    admin_location = models.BooleanField(
        blank=True,
        default=False,
        help_text="Admin locations are locations that \
        are only supposed to be used for administrative \
        and backend purposes.")

    retired = models.BooleanField(
        blank=True,
        default=False,
        help_text="Retired locations will not show up in reporting \
        but their data will remain in history.")

    headquarters = models.BooleanField(
        blank=True,
        default=False,
        help_text="Headquarters is a location where \
        boxes will be moved to when they are \
        cleaned. \
        THERE CAN ONLY BE ONE HEADQUARTER LOCATION!")

    washing_location = models.BooleanField(
        blank=True,
        default=False,
        help_text="washing_location is a location where \
        boxes are moved when they are picked up \
        from checkin locations. \
        THERE CAN ONLY BE ONE WASHING LOCATION!")

    dumping_location = models.BooleanField(
        blank=True,
        default=False,
        help_text="dumping_location is a location where \
        accidental checkout boxes are 'checked in' to. \
        THERE CAN ONLY BE ONE DUMPING LOCATION!")

    def __str__(self):
        return "{} - {} ({})".format(self.name, self.service, self.code)

    def save(self, *args, **kwargs):
        if self.headquarters or self.washing_location or self.dumping_location:
            self.admin_location = True
        else:
            self.admin_location = False
        self._set_code()
        self._geocode()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('location', kwargs={"location_code": self.code})

    def set_stock(self, count):
        return LocationStockCount.objects.create(location=self, count=count)

    @property
    def dashboard_url(self):
        from django.urls import reverse
        if self.code:
            return reverse('dashboard', kwargs={"location_code": self.code})
        else:
            return ''

    def get_estimated_stock(self):
        try:
            last_count = LocationStockCount.objects.filter(location=self).order_by('-created_at')[0]
        except IndexError:
            last_count = LocationStockCount.objects.create(location=self, count=0)

        boxes_moved = LocationTag.objects.filter(
            location=self, created_at__gt=last_count.created_at
        ).count()

        if self.service == self.CHECKOUT:
            return last_count.count - boxes_moved
        else:
            return last_count.count + boxes_moved

    def _set_code(self, force=False):
        if force or not self.code:
            shortuuid.set_alphabet("23456789ABCDEFGHJKLMNPQRSTUVWXYZ")
            code = shortuuid.uuid()[:6]
            while Location.objects.filter(code=code).count() > 0:
                code = shortuuid.uuid()[:6]
            self.code = code

    def _geocode(self):
        if self.address:
            result = geocode(self.address, provider='google')
            if result.latlng:
                lat, lng = result.latlng
                self.latitude = lat
                self.longitude = lng

    @property
    def total_uses(self):
        return LocationTag.objects.filter(location=self).count()

    @property
    def error_percentage(self):
        try:
            if self.service != 'OUT' or self.admin_location:
                return 'NA'
            error_difference_list = [abs(report.actual_amount - report.estimated_amount) for report in LocationStockReport.objects.filter(location_id=self.id, created_at__range=(timezone.now() - timedelta(weeks=12), timezone.now()))]
            if not error_difference_list:
                return None
            percent_correct = int((error_difference_list.count(0)/len(error_difference_list)) * 100)
            percent_incorrect = 100 - percent_correct
            return percent_incorrect
        except Exception as ex:
            rollbar.report_exc_info(sys.exc_info(), ex)
            return 'ERROR'

    @property
    def error_avg_difference(self):
        try:
            if self.service != 'OUT' or self.admin_location:
                return 'NA'
            error_difference_list = [abs(report.actual_amount - report.estimated_amount) for report in LocationStockReport.objects.filter(location_id=self.id)]
            if not error_difference_list:
                return None
            avg_difference = int(sum(error_difference_list)/len(error_difference_list))
            return avg_difference
        except Exception as ex:
            rollbar.report_exc_info(sys.exc_info(), ex)
            return 'ERROR'

    @property
    def error_rate(self):
        try:
            if self.error_percentage == 'ERROR' or self.error_avg_difference == 'ERROR':
                return 'ERROR'
            if self.error_percentage == 'NA' or self.error_avg_difference == 'NA':
                return 'NA'
            if self.error_percentage:
                return '{}% of the time, the count is about {} boxes off'.format(self.error_percentage, self.error_avg_difference)
            else:
                return None
        except Exception as ex:
            rollbar.report_exc_info(sys.exc_info(), ex)
            return 'ERROR'


    @property
    def avg_weekly_usage_over_past_4_weeks(self):
        try:
            tags = [
                len(LocationTag.objects.filter(location=self, created_at__range=(timezone.now() - timedelta(weeks=1), timezone.now()))),
                len(LocationTag.objects.filter(location=self, created_at__range=(timezone.now() - timedelta(weeks=2), timezone.now() - timedelta(weeks=1)))),
                len(LocationTag.objects.filter(location=self, created_at__range=(timezone.now() - timedelta(weeks=3), timezone.now() - timedelta(weeks=2)))),
                len(LocationTag.objects.filter(location=self, created_at__range=(timezone.now() - timedelta(weeks=4), timezone.now() - timedelta(weeks=3)))),
            ]
            return int(sum(tags)/len(tags))
        except Exception as ex:
            rollbar.report_exc_info(sys.exc_info(), ex)
            return 'ERROR'


    @property
    def is_admin_location(self):
        if self.headquarters:
            return 'Headquarters'
        if self.washing_location:
            return 'Washing Location'
        if self.dumping_location:
            if self.service == 'IN':
                return 'Checkin Dumping Location'
            if self.service == 'OUT':
                return 'Checkout Dumping Location'
            return 'Unknown Dumping Location'
        if self.admin_location:
            return 'Unknown Admin Location'
        return ''


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


class LocationTagQuerySet(models.QuerySet):
    def tags_on_days_ago(self, days = 7):
        day = timezone.now() - timedelta(days=days)
        return self.filter(created_at__month=day.month).filter(created_at__day=day.day)

    def tags_since_days_ago(self, days = 7):
        return self.filter(
            created_at__range=(
                timezone.now() - timedelta(days=days), timezone.now()
                )
            )

    def tags_not_emailed(self):
        return self.filter(emailed=False)

    def checkin(self):
        return self.filter(location__service=Location.CHECKIN)

    def checkout(self):
        return self.filter(location__service=Location.CHECKOUT)


class LocationTag(models.Model):
    objects = LocationTagQuerySet.as_manager()

    subscription = models.ForeignKey(Subscription)
    location = models.ForeignKey(Location)
    created_at = models.DateTimeField(auto_now_add=True)
    emailed = models.BooleanField(default=False)
    item_type = models.CharField(max_length=25, choices=ITEM_CHOICES, default=BOX,)

    def __str__(self):
        return "Location Tag - {} - {}".format(self.subscription.user, self.created_at)


class LocationStockCount(models.Model):
    """
    an actual stock count at the given location
    """
    location = models.ForeignKey(Location, related_name='stock_counts')
    created_at = models.DateTimeField(auto_now_add=True)
    count = models.IntegerField()

class LocationStockReport(models.Model):
    """
    a report object of the actual and estimated box count at the given
    location
    """
    location = models.ForeignKey(Location, related_name='stock_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    actual_amount = models.IntegerField()
    estimated_amount = models.IntegerField()

    def save(self, *args, **kwargs):
        """
        Disallow editing of codes.
        Create coupon on Stripe upon creation.
        """
        if self.pk is not None:
            return
        if self.location:
            self.estimated_amount = self.location.get_estimated_stock()
        super().save(*args, **kwargs)

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=1023)
    website = models.CharField(max_length=1023, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    phase = models.PositiveIntegerField(default=1)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.address and self.latitude is None or self.longitude is None:
            result = geocode(self.address, provider='google')
            lat, lng = result.latlng
            self.latitude = lat
            self.longitude = lng
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


def one_year_from_now():
    return date.today() + timedelta(days=365)

class Reward(models.Model):
    user = models.ForeignKey(User, related_name="rewards")
    restaurant = models.ForeignKey(Location, related_name="rewards")
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField(default=5.00)
    redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(null=True, blank=True)

    def default_location(self):
        lastMonth = timezone.now() - timedelta(days=30)
        return Location.objects.getTopUsedLocation(lastMonth.month, lastMonth.year)

    def __str__(self):
        return '{} - {}'.format(self.user, self.restaurant)

    def save(self, *args, **kwargs):
        if self.redeemed and self.redeemed_at is None:
            self.redeemed_at = timezone.now()
        elif not self.redeemed and self.redeemed_at is not None:
            self.redeemed_at = None
        super().save(*args, **kwargs)

class CouponCode(models.Model):
    # TODO MAKE SURE THAT CORP CODES AND CUP CODES CANT MATCH
    coupon_name = models.CharField(max_length=100)
    emails = models.CharField(max_length=1024,
            help_text="comma separated list of emails to restrict "
            "coupon access to. Leave this blank otherwise.",
            blank=True)
    code = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9]{4,20}$",
                message="Code can only contain capitol letters and numbers " +
                "with no spaces. Must be between 4 and 20 characters."
            )
        ]
    )
    value = models.DecimalField(max_digits=5, decimal_places=2, default=25.00)
    #if True, value becomes a % off the price
    is_percentage = models.BooleanField(default=False)
    redeem_by = models.DateField(default=one_year_from_now)
    duration = models.CharField(max_length=100,
        choices=(("once","once"),("forever","forever")),
        default='once',
        help_text="This describes if the coupon should be applied once, or "
                    "every time the subscription is renewed")
    plans = models.ManyToManyField(Plan, blank=True, related_name="coupons",
            help_text="Selecting no plans to make this coupon available for all "
            "plans. ")

    def __str__(self):
        return "{} - {}".format(self.coupon_name, self.code)

    def save(self, *args, **kwargs):
        """
        Disallow editing of codes.
        Create coupon on Stripe upon creation.
        """
        if self.pk is not None:
            return

        if self.is_percentage:
            amount_or_percent = {"percent_off": int(self.value)}
        else:
            amount_or_percent = {"amount_off": int(self.value * 100)}

        coupon = stripe.Coupon.create(
            id=self.code,
            duration=self.duration,
            currency="USD",
            redeem_by=int(datetime.combine(self.redeem_by, datetime.min.time()).timestamp()),
            **amount_or_percent
        )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        coupon = stripe.Coupon.retrieve(id=self.code)
        coupon.delete()
        super().delete(*args, **kwargs)


class CorporateCode(models.Model):
    # TODO MAKE SURE THAT CORP CODES AND CUP CODES CANT MATCH
    company_name = models.CharField(max_length=100)
    code = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9]{4,20}$",
                message="Code can only contain capitol letters and numbers " +
                "with no spaces. Must be between 4 and 20 characters."
            )
        ]
    )

    amount_off = models.DecimalField(max_digits=5, decimal_places=2, default=25.00)
    redeem_by = models.DateField(default=one_year_from_now)

    def __str__(self):
        return "{} - {}".format(self.company_name, self.code)

    def save(self, *args, **kwargs):
        """
        Disallow editing of codes.
        Create coupon on Stripe upon creation.
        """
        if self.pk is not None:
            return
        coupon = stripe.Coupon.create(
            id=self.code,
            duration="once",
            amount_off=int(self.amount_off * 100),
            currency="USD",
            redeem_by=int(datetime.combine(self.redeem_by, datetime.min.time()).timestamp())
        )
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        coupon = stripe.Coupon.retrieve(id=self.code)
        coupon.delete()
        super().delete(*args, **kwargs)


# class CoporateSubscription(models.Model):
#     name = models.CharField()
#     corporate_codes = models.ManyToManyField(CorporateCode)

#     def __str__(self):
#         return self.name


class GroupOrder(models.Model):
    # corporate_subscription = models.ForeignKey(CoporateSubscription)
    subscription = models.ForeignKey(Subscription)
    corporate_code = models.ForeignKey(CorporateCode)
    location = models.ForeignKey(Location)
    expected_checkout = models.DateField(blank=True)
    count = models.IntegerField()
    checked_out = models.BooleanField(default=False)
    checked_in = models.BooleanField(default=False)
    item_type = models.CharField(max_length=25, choices=ITEM_CHOICES, default=BOX,)
    created_at = models.DateTimeField(auto_now_add=True)

    def check_out(self):
        if self.checked_out:
            return self
        checkin = Location.objects.dumping_in()
        subscription.tag_location(checkin, self.count, self.subscription.user)
        subscription.tag_location(self.location, self.count, self.subscription.user)
        self.checked_out = True
        self.save()
        return self

    def check_in(self, code):
        if self.checked_in and not self.checked_out:
            return self
        checkin = Location.objects.filter(code=code)
        checkout = Location.objects.dumping_out()
        subscription.tag_location(checkin, self.count, self.subscription.user)
        subscription.tag_location(checkout, self.count, self.subscription.user)
        self.checked_in = True
        self.save()
        return self

    def __str__(self):
        return "Group Order - {} - {}".format(self.corporate_code, self.location)
