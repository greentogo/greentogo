from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils.safestring import mark_safe

from core.models import Location, Subscription, LocationTag, User


def registration_complete(request):
    print("Heyo")
    print(request)
    activation_key = "123"
    # user = request.user
    # if not user.stripe_id:
    #     user.create_stripe_customer()
    # if request.method == "POST":
    #     location_code = request.POST.get('location_code').upper()
    #     try:
    #         location = Location.objects.get(code=location_code)
    #         return redirect(location.get_absolute_url())
    #     except Location.DoesNotExist:
    #         if location_code:
    #             messages.error(request, "There is no location that matches that code.")
    #         else:
    #             messages.error(request, "Please enter a code.")

    return render(request, "registration/registration_complete.html", {
        "activation_key": activation_key,
    })