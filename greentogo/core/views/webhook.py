import json
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.models import Subscription
from core.stripe import stripe

from templated_email import send_templated_mail

import datetime

import rollbar

endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
logger = logging.getLogger('django')
User = get_user_model()

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
        return HttpResponse(status=401)

    logger.info(payload)

    # Do something with event
    if event.type in handlers:
        handlers[event.type](event)

    return HttpResponse(status=200)


@handle_event('customer.subscription.deleted')
def handle_customer_subscription_deleted(event):
    event_sub = event.data.object

    subscription = Subscription.objects.filter(stripe_id=event_sub.id).first()
    if not subscription:
        logger.warn(
            "Subscription {} not found for customer.subscription.deleted webhook".
            format(event_sub.id)
        )
        return

    subscription.sync_with_stripe(event_sub)


@handle_event('customer.subscription.updated')
def handle_subscription_updated(event):
    """When a subscription is updated, update it in our DB."""
    event_sub = event.data.object

    subscription = Subscription.objects.filter(stripe_id=event_sub.id).first()
    if not subscription:
        logger.warn(
            "Subscription {} not found for customer.subscription.updated webhook".
            format(event_sub.id)
        )
        return

    subscription.sync_with_stripe(event_sub)


@handle_event('invoice.payment_succeeded')
def handle_invoice_payment_succeeded(event):
    """When an invoice payment is successful, update the subscription ends_at and status."""
    # TODO send an email to customer
    invoice = event.data.object
    customer = User.objects.filter(stripe_id=invoice.customer).first()
    if not customer:
        return logger.warn(
            "Customer {} not found for invoice.payment_succeeded webhook".format(invoice.customer)
        )

    if not invoice.lines.data:
        return
    for line in invoice.lines.data:
        if line.id.startswith("sub_"):
            try:
                subscription = Subscription.objects.filter(stripe_id=line.id).first()
                if not subscription:
                    logger.warn("Subscription {} not found for invoice.payment_succeeded webhook".format(line.id))
                subscription.sync_with_stripe()
            except Exception as ex:
                rollbar.report_message(ex, "error")
                logger.error(ex)


@handle_event('invoice.payment_failed')
def handle_invoice_payment_failed(event):
    """When an invoice payment fails, let the customer know and update their subscription (how?)"""
    # TODO send an email to customer
    invoice = event.data.object
    customer = User.objects.filter(stripe_id=invoice.customer).first()
    if not customer:
        logger.warn(
            "Customer {} not found for invoice.payment_failed webhook".format(invoice.customer)
        )
        return

    if not invoice.lines.data:
        return
    for line in invoice.lines.data:
        if line.id.startswith("sub_"):
            subscription = Subscription.objects.filter(stripe_id=line.id).first()
            if not subscription:
                logger.warn(
                    "Subscription {} not found for invoice.payment_failed webhook".format(line.id)
                )
            subscription.sync_with_stripe()

@handle_event('invoice.upcoming')
def handle_invoice_upcoming(event):
    """When an invoice is upcoming, let the customer know by email"""
    customer = None

    invoice = event.data.object

    # Invoice lines have a list that should include one subscription id that we can use
    subObj = Subscription.objects.filter(stripe_id=invoice.lines.data[0].id).first()

    if subObj:
        customer = subObj.user
    else:
        customer = User.objects.filter(stripe_id=invoice.customer).first()

    if not customer:
        custNotFoundMessage = "Customer {} not found for invoice.upcoming webhook".format(invoice.customer)
        logger.error(custNotFoundMessage)
        rollbar.report_message(custNotFoundMessage, "error")
        return

    # Send email to customer if invoice needs payment
    try:
        if customer.email:
            #convert the date to readable string
            if invoice.next_payment_attempt:
                renew_date = datetime.datetime.fromtimestamp(
                    int(invoice.next_payment_attempt)
                ).strftime('%B %d')
            else:
                dateNotFoundMessage = "next_payment_attempt was null, hardcoding upcoming invoice plus seven days"
                logger.error(dateNotFoundMessage)
                rollbar.report_message(dateNotFoundMessage, "error")
                renew_date =  datetime.datetime.fromtimestamp(
                    int(invoice.date) + 604800
                ).strftime('%B %d')

            site = Site.objects.get_current()

            amountDue = int(invoice.amount_due) / 100
            
            send_templated_mail(
                template_name='upcoming_invoice',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[customer.email,],
                context={
                        'renew_date': renew_date,
                        'amount_due': amountDue,
                        'site': site
                    }
            )
        else:
            userMissingEmailMessage = "invoice.upcoming webhook fail for user {} - user did not have email".format(invoice.customer)
            logger.error(userMissingEmailMessage)
            rollbar.report_message(userMissingEmailMessage, "error")
    except Exception as e:
        genericErrorMessage = "invoice.upcoming webhook fail for user {} - generic exception".format(invoice.customer)
        logger.error(genericErrorMessage)
        rollbar.report_message(genericErrorMessage, "error")
        raise e
