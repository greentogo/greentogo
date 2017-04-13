import json
from collections import OrderedDict
from itertools import groupby

import pinax.stripe.models as pinax_models
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST
from pinax.stripe.actions import customers, invoices, sources, subscriptions

from .forms import NewSubscriptionForm, SubscriptionForm, SubscriptionPlanForm, UserForm
from .models import Location, Restaurant, Subscription, SubscriptionInvitation, get_plans


def index(request):
    return render(request, 'core/index_logged_out.html')


@login_required
def account(request):
    if request.method == "POST":
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            messages.success(request, "You have updated your user information.")
            form.save()
            return redirect(reverse("account"))
    else:
        form = UserForm(instance=request.user)

    subscriptions = request.user.subscriptions.active().reverse_chrono_order()

    return render(request, 'core/account.html', {"form": form, "subscriptions": subscriptions})


@login_required
def change_password(request):
    if request.method == "POST":
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed.")
            return redirect(reverse('account'))
    else:
        form = SetPasswordForm(request.user)

    return render(request, "core/change_password.html", {"form": form})


@login_required
def change_payment_method(request):
    customer = request.user.customer
    card = pinax_models.Card.objects.get(stripe_id=customer.default_source)
    if request.method == "POST":
        token = request.POST.get('token')
        if token:
            try:
                source = sources.create_card(customer=customer, token=token)
                customers.set_default_source(customer=customer, source=source)
                messages.success(request, "You have updated your default payment source.")
                return redirect(reverse('account'))
            except stripe.error.CardError as ex:
                error = ex.json_body.get('error')
                messages.error(
                    request, "We had a problem processing your card. {}".format(error['message'])
                )

    return render(
        request, "core/change_payment_source.html",
        {"card": card,
         "stripe_key": settings.STRIPE_PUBLISHABLE_KEY}
    )


@login_required
def subscription(request, sub_id):
    subscription = request.user.subscriptions.get(pinax_subscription__stripe_id=sub_id)
    if request.method == "POST":
        form = SubscriptionForm(request.POST, instance=subscription)
        if form.is_valid():
            form.save()
            messages.success(request, "You have updated your subscription.")
            return redirect(reverse('account'))
    else:
        form = SubscriptionForm(instance=subscription)

    return render(
        request, "core/subscription.html", {
            "form": form,
            "subscription": subscription,
        }
    )


@login_required
def add_subscription(request):
    if request.method == "POST":
        form = NewSubscriptionForm(request.POST)
        if form.is_valid():
            plan = pinax_models.Plan.objects.get(stripe_id=form.cleaned_data['plan'])
            try:
                subscriptions.create(
                    customer=request.user.customer, plan=plan, token=form.cleaned_data['token']
                )
                messages.success(
                    request, "You have added a subscription to the plan {}.".format(plan.name)
                )
                return redirect(reverse('account'))
            except stripe.error.CardError as ex:
                error = ex.json_body.get('error')
                messages.error(
                    request, "We had a problem processing your card. {}".format(error['message'])
                )
    else:
        form = NewSubscriptionForm()

    return render(
        request, "core/add_subscription.html", {
            "form": form,
            "plans": get_plans(),
            "email": request.user.email,
            "stripe_key": settings.STRIPE_PUBLISHABLE_KEY
        }
    )


@login_required
def change_subscription_plan(request, sub_id):
    customer = request.user.customer
    subscription = Subscription.lookup_by_customer_and_sub_id(customer, sub_id)
    if request.method == "POST":
        form = SubscriptionPlanForm(request.POST)
        if form.is_valid():
            plan = pinax_models.Plan.objects.get(stripe_id=form.cleaned_data['plan'])
            subscriptions.update(
                subscription=subscription.pinax_subscription,
                plan=plan,
                prorate=True,
                charge_immediately=True
            )
            invoices.create(customer=customer)
            messages.success(request, "Your plan has been updated to {}.".format(plan.name))
            return redirect(reverse('account'))
    else:
        form = SubscriptionPlanForm()

    return render(
        request, "core/subscription_plan.html", {"subscription": subscription,
                                                 "form": form}
    )


@login_required
def cancel_subscription(request, sub_id):
    subscription = Subscription.lookup_by_customer_and_sub_id(request.user.customer, sub_id)
    if request.method == "POST":
        subscription.cancel()
        messages.success(request, "Your subscription has been cancelled.")
        return redirect(reverse('account'))

    return render(request, "core/cancel_subscription.html", {"subscription": subscription})


def restaurants(request):
    restaurants = Restaurant.objects.order_by('phase', 'name').all()
    restaurants_by_phase = OrderedDict()
    phases = []
    for phase, rlist in groupby((r for r in restaurants), key=lambda r: r.phase):
        phases.append(phase)
        restaurants_by_phase[phase] = [r for r in rlist]
    phase_colors = {1: 'red', 2: 'blue', 3: 'purple', 4: 'yellow', 5: 'green'}

    return render(
        request, "core/restaurants.djhtml", {
            "api_key": settings.GOOGLE_API_KEY,
            "phases": phases,
            "phase_colors": phase_colors,
            "phase_colors_json": mark_safe(json.dumps(phase_colors)),
            "restaurants_by_phase": restaurants_by_phase,
            "restaurants_json": mark_safe(serializers.serialize("json", restaurants))
        }
    )


@login_required
def locations(request):
    if request.method == "POST":
        location_code = request.POST.get('location_code').upper()
        try:
            location = Location.objects.get(code=location_code)
            return redirect(reverse('location', kwargs={"location_code": location_code}))
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


@login_required
def invitation(request, invitation_code):
    user = request.user
    invitation = get_object_or_404(SubscriptionInvitation, code=invitation_code)

    subscription = invitation.accept(user)
    messages.success(
        request, "You have accepted an invitation to {}'s {} subscription.".format(
            subscription.owner.name, subscription.plan_display()
        )
    )

    return redirect(reverse('account'))
