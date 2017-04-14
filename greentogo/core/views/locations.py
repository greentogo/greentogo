from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe

from core.models import Location, Subscription


@login_required
def locations(request):
    if request.method == "POST":
        location_code = request.POST.get('location_code').upper()
        try:
            location = Location.objects.get(code=location_code)
            return redirect(location.get_absolute_url())
        except Location.DoesNotExist:
            if location_code:
                messages.error(request, "There is no location that matches that code.")
            else:
                messages.error(request, "Please enter a code.")

    return render(request, "core/locations.djhtml")


@login_required
def location(request, location_code):
    user = request.user
    location = get_object_or_404(Location, code=location_code.upper())

    if request.method == "POST":
        subscription_id = request.POST.get('subscription_id')
        try:
            subscription = user.subscriptions.active().get(pk=subscription_id)
        except Subscription.DoesNotExist as ex:
            # TODO: handle this
            raise ex

        with transaction.atomic():
            if subscription.can_tag_location(location):
                subscription.tag_location(location)
                if location.service == location.CHECKIN:
                    msg = "You have checked in 1 box."
                else:
                    msg = "You have checked out 1 box."
                messages.success(request, msg)
            else:
                if location.service == location.CHECKIN:
                    msg = "You have checked in all of your boxes for this subscription."
                else:
                    msg = "You do not have enough boxes to check out with this subscription."
                    if subscription.is_owner_subscription():
                        msg += """ <a href="{}">Change your subscription plan.</a>""".format(
                            reverse('subscription_plan', kwargs={"sub_id": subscription.stripe_id})
                        )
                        msg = mark_safe(msg)

                messages.error(request, msg)

    subscriptions = [
        {
            "id": subscription.pk,
            "name": subscription.plan_display(),
            "max_boxes": subscription.number_of_boxes,
            "available_boxes": subscription.available_boxes(),
        } for subscription in user.subscriptions.active()
    ]

    return render(
        request, "core/location.djhtml", {
            "location": location,
            "subscriptions": subscriptions,
        }
    )
