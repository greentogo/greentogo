from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from pinax.stripe.actions import invoices, customers, subscriptions

from .models import Subscription


def index(request):
    return render(request, 'core/index_logged_out.html')


@login_required
def account(request):
    customer = request.user.customer
    subscriptions = [{
        "id": subscription.stripe_id,
        "name": subscription.plan_display(),
        "ends": subscription.current_period_end,
    }
                     for subscription in customer.subscription_set.filter(
                         ended_at=None, canceled_at=None)]

    return render(request, 'core/account.html',
                  {"customer": customer,
                   "subscriptions": subscriptions})


@login_required
def subscription(request, sub_id):
    subscription = Subscription.lookup_by_customer_and_sub_id(
        request.user.customer, sub_id)
    return render(request, "core/subscription.html", {
        "subscription": subscription,
    })


@login_required
@require_POST
def cancel_subscription(request, sub_id):
    # TODO add messaging
    subscription = Subscription.lookup_by_customer_and_sub_id(
        request.user.customer, sub_id)
    subscriptions.cancel(subscription, at_period_end=False)
    return redirect(reverse('account'))
