from django.shortcuts import render
from django.contrib.auth.decorators import login_required
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
    # TODO handle exceptions
    subscription = request.user.customer.subscription_set.get(stripe_id=sub_id)
    subscription = Subscription.from_pinax(subscription)
    return render(request, "core/subscription.html", {
        "subscription": subscription,
    })
