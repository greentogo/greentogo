from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

import stripe

from core.forms import NewSubscriptionForm, SubscriptionForm, SubscriptionPlanForm
from core.models import Subscription, get_plans


@login_required
def subscriptions_view(request):
    subscriptions = request.user.subscriptions.active().order_by("starts_at")
    return render(request, 'core/subscriptions.html', {"subscriptions": subscriptions})


@login_required
def subscription(request, sub_id):
    sub = request.user.subscriptions.get(pinax_subscription__stripe_id=sub_id)
    if request.method == "POST":
        form = SubscriptionForm(request.POST, instance=sub)
        if form.is_valid():
            form.save()
            messages.success(request, "You have updated your subscription.")
            return redirect(reverse('subscriptions'))
    else:
        form = SubscriptionForm(instance=sub)

    return render(
        request, "core/subscription.html", {
            "form": form,
            "invite_form": invite_form,
            "invitations": invitations,
            "subscription": sub,
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
                return redirect(reverse('subscriptions'))
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
            return redirect(reverse('subscriptions'))
    else:
        form = SubscriptionPlanForm()

    return render(
        request, "core/subscription_plan.html", {"subscription": subscription,
                                                 "form": form}
    )
