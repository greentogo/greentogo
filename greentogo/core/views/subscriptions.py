import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from pinax.stripe import models as pinax_models
from pinax.stripe.actions import invoices, subscriptions

from core.forms import (
    NewSubscriptionForm, SubscriptionForm, SubscriptionInvitationForm, SubscriptionPlanForm
)
from core.models import Subscription, SubscriptionInvitation, get_plans


@login_required
def subscription(request, sub_id):
    sub = request.user.subscriptions.get(pinax_subscription__stripe_id=sub_id)
    if request.method == "POST":
        form = SubscriptionForm(request.POST, instance=sub)
        if form.is_valid():
            form.save()
            messages.success(request, "You have updated your subscription.")
            return redirect(reverse('account'))
    else:
        form = SubscriptionForm(instance=sub)
        invite_form = SubscriptionInvitationForm()
        invitations = SubscriptionInvitation.objects.filter(
            pinax_subscription=sub.pinax_subscription
        )

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


@login_required
@require_POST
def create_invite(request, sub_id):
    customer = request.user.customer
    sub = Subscription.lookup_by_customer_and_sub_id(customer, sub_id)
    # TODO handle people going to the wrong subscription

    form = SubscriptionInvitationForm(request.POST)
    if form.is_valid():
        invite, _ = SubscriptionInvitation.objects.get_or_create(
            pinax_subscription=sub.pinax_subscription, **form.cleaned_data
        )
        invite.send_invitation()
        messages.success(
            request, """You have invited {} to share your subscription "{}".""".format(
                form.cleaned_data['email'], sub.display_name
            )
        )
    else:
        messages.error(request, "There was a problem completing your invitation.")

    return redirect(reverse('subscription', kwargs=dict(sub_id=sub.stripe_id)))
