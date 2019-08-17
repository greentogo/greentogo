import rollbar, sys
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils import timezone

from core.models import Subscription


class Command(BaseCommand):
    help = "Command to send emails to people who have not checked in boxes"

    def handle(self, *args, **options):
      subs = Subscription.objects.filter(cancelled=True, stripe_status='active')
      print(subs)
      for sub in subs:
        try:
          print('Cancelling:')
          print(sub)
          stripe_sub = sub.get_stripe_subscription()
          stripe_sub.delete(at_period_end = True)
        except Exception as ex:
          print('UNABLE TO CANCEL:')
          print(sub)
          print(ex)