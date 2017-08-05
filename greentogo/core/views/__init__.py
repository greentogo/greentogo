import json
from collections import OrderedDict
from itertools import groupby

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import stripe

from ..forms import UserForm
from ..models import Restaurant


def index(request):
    return render(request, 'core/index_logged_out.html')


@login_required
def account_settings(request):
    if request.method == "POST":
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            messages.success(request, "You have updated your user information.")
            form.save()
            return redirect(reverse("account_settings"))
    else:
        form = UserForm(instance=request.user)

    return render(request, 'core/account.html', {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed.")
            return redirect(reverse('account_settings'))
    else:
        form = SetPasswordForm(request.user)

    return render(request, "core/change_password.html", {"form": form})


def first(lst, predicate):
    for x in lst:
        if predicate(x): return x
    return None


@login_required
def change_payment_method(request):
    user = request.user
    customer = user.get_stripe_customer(create=True)

    card = None
    if customer.default_source:
        card = first(customer.sources.data, lambda source: source.id == customer.default_source)

    if request.method == "POST":
        token = request.POST.get('token')
        if token:
            try:
                customer.source = token
                customer.save()
                messages.success(request, "You have updated your default payment source.")
                return redirect(reverse('account_settings'))
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
