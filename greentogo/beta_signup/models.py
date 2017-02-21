import uuid

from django.db import models
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from pinax.stripe import models as pinax_models

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


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


def send_subscriber_email(subscription):
    plan = plan_to_dict(subscription.plan)
    body = render_to_string("email/new_subscriber.txt",
                            {"subscription": subscription,
                             "plan": plan})
    msg = EmailMessage(
        subject="Thank you for subscribing to Durham GreenToGo!",
        body=body,
        from_email=settings.EMAIL_HOST_USER,
        to=[subscription.customer.user.email],
        reply_to=[settings.EMAIL_REPLY_TO])
    msg.send()


def send_admin_email(subscription):
    plan = plan_to_dict(subscription.plan)
    body = render_to_string("email/new_subscriber_admin.txt",
                            {"subscription": subscription,
                             "plan": plan})
    msg = EmailMessage(
        subject="New GreenToGo subscriber",
        body=body,
        from_email=settings.EMAIL_HOST_USER,
        to=settings.EMAIL_ADMINS,
        reply_to=[settings.EMAIL_REPLY_TO])
    msg.send()


class GiftSubscription(models.Model):
    stripe_subscription = models.OneToOneField(pinax_models.Subscription)
    gifted_to_name = models.CharField(max_length=255, blank=True)
    gifted_to_email = models.CharField(max_length=255, blank=True)
