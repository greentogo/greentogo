import uuid

from django.db import models
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def get_plan_price(plan):
    """Given a Stripe plan, get the price as it should be printed."""
    if plan['currency'] == 'usd':
        price = "${:.02f}".format(plan['amount'] / 100)
        if price.endswith(".00"):
            price = price[:-3]
    return price


def add_plan_price(plan):
    """Given a Stripe plan, set the price as it should be printed."""
    plan['display_price'] = get_plan_price(plan)
    return plan


class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    stripe_id = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    stripe_id = models.CharField(max_length=100, unique=True)
    internal_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    customer = models.ForeignKey(Customer)
    plan = models.CharField(max_length=255)
    gifted_to_name = models.CharField(max_length=255, blank=True)
    gifted_to_email = models.CharField(max_length=255, blank=True)
    started_on = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        result = super().save(*args, **kwargs)

        if is_new:
            self.send_subscriber_email()
            self.send_admin_email()

        return result

    def get_plan_details(self):
        details = stripe.Plan.retrieve(self.plan)
        return details

    def send_subscriber_email(self):
        plan = self.get_plan_details()
        plan['display_price'] = get_plan_price(plan)
        body = render_to_string(
            "email/new_subscriber.txt", {"subscription": self, "plan": plan})
        msg = EmailMessage(
            subject="Thank you for subscribing to Durham GreenToGo!",
            body=body,
            from_email=settings.EMAIL_HOST_USER,
            to=[self.customer.email],
            reply_to=[settings.EMAIL_REPLY_TO]
        )
        msg.send()

    def send_admin_email(self):
        plan = self.get_plan_details()
        plan['display_price'] = get_plan_price(plan)
        body = render_to_string(
            "email/new_subscriber_admin.txt", {"subscription": self, "plan": plan})
        msg = EmailMessage(
            subject="New GreenToGo subscriber",
            body=body,
            from_email=settings.EMAIL_HOST_USER,
            to=settings.EMAIL_ADMINS,
            reply_to=[settings.EMAIL_REPLY_TO]
        )
        msg.send()
