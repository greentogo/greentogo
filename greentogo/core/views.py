from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from pinax.stripe.actions import invoices, customers, subscriptions
import pinax.stripe.models as pinax_models
from .models import Subscription, get_plans
from .forms import SubscriptionPlanForm


def index(request):
    return render(request, 'core/index_logged_out.html')


@login_required
def account(request):
    customer = request.user.customer
    subscriptions = [
        {
            "id": subscription.stripe_id,
            "name": subscription.plan_display(),
            "price": subscription.total_amount,
            "ends": subscription.current_period_end,
            "auto_renew": not subscription.cancel_at_period_end,
        }
        for subscription in customer.subscription_set.filter(ended_at=None)
        .order_by("-current_period_end")
    ]

    return render(
        request, 'core/account.html', {"customer": customer,
                                       "subscriptions": subscriptions}
    )


@login_required
def subscription(request, sub_id):
    subscription = Subscription.lookup_by_customer_and_sub_id(request.user.customer, sub_id)
    return render(request, "core/subscription.html", {
        "subscription": subscription,
    })


@login_required
def subscription_plan(request, sub_id):
    subscription = Subscription.lookup_by_customer_and_sub_id(request.user.customer, sub_id)
    if request.method == "POST":
        form = SubscriptionPlanForm(request.POST)
        if form.is_valid():
            plan = pinax_models.Plan.objects.get(stripe_id=form.cleaned_data['plan'])
            subscriptions.update(
                subscription=subscription, plan=plan, prorate=True, charge_immediately=True
            )
            messages.success(request, "Your plan has been updated to {}.".format(plan.name))
            return redirect(reverse('account'))
    else:
        form = SubscriptionPlanForm()

    return render(
        request, "core/subscription_plan.html", {"subscription": subscription,
                                                 "form": form}
    )


@login_required
@require_POST
def cancel_subscription(request, sub_id):
    # TODO add messaging
    subscription = Subscription.lookup_by_customer_and_sub_id(request.user.customer, sub_id)
    subscriptions.cancel(subscription, at_period_end=False)
    return redirect(reverse('account'))
