import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.models import Subscription
from core.stripe import stripe

endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
logger = logging.getLogger('django')

handlers = {}


def handle_event(event_name):
    def handler_decorator(func):
        handlers[event_name] = func
        return func

    return handler_decorator


@require_POST
@csrf_exempt
def stripe_webhook(request):
    payload = request.body.decode("utf-8")
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Do something with event
    if event.type in handlers:
        handlers[event.type](event)

    return HttpResponse(status=200)


@handle_event('customer.subscription.deleted')
def handle_customer_subscription_deleted(event):
    event_sub = event.data.object

    subscription = Subscription.objects.filter(stripe_id=event_sub.id).first()
    if not subscription:
        return

    subscription.ends_at = event_sub.ended_at
    subscription.stripe_status = event_sub.status
    subscription.save()

    logger.info("Subscription found")


@handle_event('invoice.payment_succeeded')
def handle_invoice_payment_succeeded(event):
    """When an invoice payment is successful, update the subscription ends_at and status."""


@handle_event('invoice.payment_failed')
def handle_invoice_payment_failed(event):
    """When an invoice payment fails, let the customer know and update their subscription (how?)"""
    """
    $customer = \Stripe\Customer::retrieve($event->data->object->customer);
    $email = $customer->email;
    // Sending your customers the amount in pennies is weird, so convert to dollars
    $amount = sprintf('$%0.2f', $event->data->object->amount_due / 100.0);
    """


@handle_event('customer.subscription.updated')
def handle_subscription_updated(event):
    """When a subscription is updated, update it in our DB."""
