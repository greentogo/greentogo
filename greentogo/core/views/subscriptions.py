from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

import stripe

from core.forms import NewSubscriptionForm, SubscriptionForm, SubscriptionPlanForm
from core.models import Plan, Subscription
from core.utils import decode_id, encode_nums


@login_required
def subscriptions_view(request):
    subscriptions = request.user.subscriptions.active().order_by("starts_at")
    return render(request, 'core/subscriptions.html', {"subscriptions": subscriptions})


@login_required
def add_subscription(request):
    if request.method == "POST":
        form = NewSubscriptionForm(request.POST)
        if form.is_valid():
            # if customer does not have a stripe_id
            #    create a customer from token
            # if customer does have a stripe_id
            #    update source with token?
            # create a subscription with customer, plan, and token
            # on failure, let customer know

            plan_stripe_id = form.cleaned_data['plan']
            token = form.cleaned_data['token']

            plan = Plan.objects.get(stripe_id=plan_stripe_id)
            # TODO handle no plan
            user = request.user

            if not user.stripe_id:
                user.create_stripe_customer(form.cleaned_data['token'])

            try:
                stripe_subscription = stripe.Subscription.create(
                    customer=user.stripe_id, source=token, items=[{
                        "plan": plan_stripe_id
                    }]
                )
                subscription = Subscription.create_from_stripe_sub(
                    user=user,
                    plan=plan,
                    stripe_subscription=stripe_subscription,
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
            "plans": Plan.objects.available(),
            "email": request.user.email,
            "stripe_key": settings.STRIPE_PUBLISHABLE_KEY
        }
    )


@login_required
def change_subscription_plan(request, sub_id):
    real_id = decode_id(sub_id)[0]
    user = request.user
    subscription = user.subscriptions.get(id=real_id)
    if request.method == "POST":
        form = SubscriptionPlanForm(request.POST)
        if form.is_valid():
            plan = Plan.objects.get(id=form.cleaned_data['plan'])
            stripe_sub = subscription.get_stripe_subscription()

            if not stripe_sub:
                messages.error(request, "You cannot update a non-billing plan.")
                return redirect(reverse('subscriptions'))

            item_id = stripe_sub['items']['data'][0].id
            stripe.Subscription.modify(
                stripe_sub.id, items=[{
                    "id": item_id,
                    "plan": plan.stripe_id
                }]
            )
            subscription.plan = plan
            subscription.save()

            messages.success(request, "Your plan has been updated to {}.".format(plan.name))
            return redirect(reverse('subscriptions'))
    else:
        form = SubscriptionPlanForm()

    return render(
        request, "core/subscription_plan.html", {"subscription": subscription,
                                                 "form": form}
    )
