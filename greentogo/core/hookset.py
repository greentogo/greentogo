from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from pinax.stripe.hooks import DefaultHookSet


class StripeHookset(DefaultHookSet):
    def send_receipt(self, charge, email=None):
        from django.conf import settings
        if not charge.receipt_sent:
            # Import here to not add a hard dependency on the Sites framework
            from django.contrib.sites.models import Site

            customer = charge.customer
            subscription = customer.subscription_set.order_by('-created_at').first()
            last4 = charge.stripe_charge.source.last4

            site = Site.objects.get_current()
            protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
            ctx = {
                "last4": last4,
                "subscription": subscription,
                "charge": charge,
                "site": site,
                "protocol": protocol,
            }
            subject = render_to_string("pinax/stripe/email/subject.txt", ctx)
            subject = subject.strip()
            message = render_to_string("email/receipt.txt", ctx)

            if not email and charge.customer:
                email = charge.customer.user.email

            num_sent = EmailMessage(
                subject, message, to=[email], from_email=settings.PINAX_STRIPE_INVOICE_FROM_EMAIL
            ).send()
            charge.receipt_sent = num_sent > 0
            charge.save()
