import rollbar, sys
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from core.models import LocationTag, User, send_push_message


class Command(BaseCommand):
    help = "Command to send emails to people who have not checked in boxes"

    def handle(self, *args, **options):
      try:
        days = 7
        users_that_have_checkin_since_last_week = LocationTag.objects.all().checkin().tags_since_days_ago(days).values('subscription__user').distinct()
        checkouts_one_week_ago = LocationTag.objects.all().checkout().tags_on_days_ago(days).tags_not_emailed()

        users_that_havent_checkedin = User.objects.filter(
            id__in=checkouts_one_week_ago.values('subscription__user').distinct()
          ).exclude(
            id__in=users_that_have_checkin_since_last_week
          )

        print(users_that_havent_checkedin)
        for user in users_that_havent_checkedin:
          checkout = checkouts_one_week_ago.filter(subscription__user=user).first()
          print('{} has not checked in since they checked out at {}'.format(user.name,checkout.location.name))
          # checkout.emailed = True
          # checkout.save()
          # EmailMessage(
          #     subject='GreenToGo Box Notification',
          #     body=render_to_string('email/box_reminder.txt', {
          #       'user': user,
          #       'checkout': checkout,
          #     }),
          #     from_email='greentogo@app.durhamgreentogo.com',
          #     to=[user.email],
          #     reply_to=["amy@durhamgreentogo.com"]
          # ).send()
          # if (user.expoPushToken):
          #   send_push_message(user.expoPushToken, 'Box Reminder!', 'Dont forget to check in your boxes!')
      except Exception as ex:
            rollbar.report_exc_info(sys.exc_info(), ex)
