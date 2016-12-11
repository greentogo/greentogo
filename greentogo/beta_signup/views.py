from django.views.generic import TemplateView
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def add_plan_price(plan):
    """Given a Stripe plan, set the price as it should be printed."""
    if plan['currency'] == 'usd':
        plan['display_price'] = "${:.02f}".format(plan['amount'] / 100)
        if plan['display_price'].endswith(".00"):
            plan['display_price'] = plan['display_price'][:-3]
    return plan


def get_plans():
    plans = sorted(stripe.Plan.list()['data'], key=lambda p: p['amount'])
    return [add_plan_price(plan) for plan in plans]


class SubscriptionView(TemplateView):
    template_name = "subscription.html"

    def get_context_data(self, **kwargs):
        context = super(SubscriptionView, self).get_context_data(**kwargs)
        context['plans'] = get_plans()
        context['stripe_key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context
