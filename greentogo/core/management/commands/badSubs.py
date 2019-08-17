import rollbar, sys
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils import timezone

from core.models import Subscription


class Command(BaseCommand):
    help = "Command to send emails to people who have not checked in boxes"

    def handle(self, *args, **options):
      stuff = Subscription.objects.filter(cancelled=True, stripe_status='active')
      print(stuff)
