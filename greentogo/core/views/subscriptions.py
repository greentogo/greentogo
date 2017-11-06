import json
import sys
from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

import rollbar
import stripe

from core.forms import NewSubscriptionForm, SubscriptionForm, SubscriptionPlanForm
from core.models import CorporateCode, Plan, Subscription
from core.utils import decode_id, encode_nums

rollbar.init(settings.ROLLBAR_KEY, settings.ROLLBAR_ENV)


@login_required
def subscriptions_view(request):
    subscriptions = request.user.subscriptions.active().order_by("starts_at")
    return render(request, 'core/subscriptions.html', {"subscriptions": subscriptions})


@login_required
def add_subscription(request, *args, **kwargs):
    corporate_code = None
    if 'code' in kwargs:
        corporate_code = get_object_or_404(CorporateCode, code=kwargs['code'])

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
                user.create_stripe_customer()

            sub_kwargs = {
                "customer": user.stripe_id,
                "source": token,
                "items": [{
                    "plan": plan_stripe_id
                }]
            }

            if corporate_code:
                sub_kwargs['coupon'] = corporate_code.code

            try:
                stripe_subscription = stripe.Subscription.create(**sub_kwargs)
                subscription = Subscription.create_from_stripe_sub(
                    user=user,
                    plan=plan,
                    stripe_subscription=stripe_subscription,
                    corporate_code=corporate_code
                )
                return redirect(reverse('subscriptions'))
            except stripe.error.CardError as ex:
                error = ex.json_body.get('error')
                messages.error(
                    request, "We had a problem processing your card. {}".format(error['message'])
                )
                rollbar.report_exc_info(sys.exc_info(), request)
            except Exception as ex:
                messages.error(
                    request, (
                        "We had a problem on our end processing your order. "
                        "You have not been charged. Our administrators have been notified."
                    )
                )
                rollbar.report_exc_info(sys.exc_info(), request)

    plans = [
        {
            'stripe_id': plan.stripe_id,
            'amount': plan.amount,
            'display_price': plan.display_price(corporate_code),
            'name': plan.name,
        } for plan in Plan.objects.available()
    ]

    plandict = {plan['stripe_id']: plan for plan in plans}

    return render(
        request, "core/add_subscription.html", {
            "form": NewSubscriptionForm(),
            "corporate_code": corporate_code,
            "plans": plans,
            "plandict_json": json.dumps(plandict, cls=DjangoJSONEncoder),
            "email": request.user.email,
            "stripe_key": settings.STRIPE_PUBLISHABLE_KEY
        }
    )


@login_required
def corporate_subscription(request, *args, **kwargs):
    """Check corporate code to see if valid."""
    if request.method == "POST":
        try:
            code = CorporateCode.objects.get(code=request.POST['code'])
            if request.user.subscriptions.filter(corporate_code=code).count() == 0:
                return redirect(reverse('add_corporate_subscription', kwargs={'code': code.code}))
            else:
                messages.error(request, "You have already used that corporate access code.")
        except CorporateCode.DoesNotExist:
            messages.error(request, "That is not a valid corporate access code.")

    return render(request, "core/corporate_subscription.html")


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
                }], prorate=True
            )

            subscription.plan = plan
            subscription.save()

            messages.success(request, "Your plan has been updated to {}.".format(plan.name))
            return redirect(reverse('subscriptions'))
    else:
        form = SubscriptionPlanForm()

    plans = [
        {
            'id': plan.pk,
            'stripe_id': plan.stripe_id,
            'amount': plan.amount,
            'display_price': plan.display_price(subscription.corporate_code),
            'name': plan.name,
        } for plan in Plan.objects.available()
    ]

    return render(
        request, "core/subscription_plan.html", {
            "subscription": subscription,
            "form": form,
            "plans": plans,
        }
    )


def add_credit_card(request, sub_id):
    real_id = decode_id(sub_id)[0]
    user = request.user
    subscription = user.subscriptions.get(id=real_id)

    if request.method == "POST":
        token = request.POST['token']
        if token:
            plan = subscription.plan

            if not user.stripe_id:
                user.create_stripe_customer()

            sub_kwargs = {
                "customer": user.stripe_id,
                "source": token,
                "items": [{
                    "plan": plan.stripe_id
                }],
                "trial_end": int(subscription.one_year_from_start().timestamp()),
            }

            try:
                stripe_subscription = stripe.Subscription.create(**sub_kwargs)
                subscription.update_from_stripe_sub(stripe_subscription)

                messages.success(
                    request, "Your credit card was added to your subscription successfully."
                )
                return redirect(reverse('subscriptions'))
            except stripe.error.CardError as ex:
                error = ex.json_body.get('error')
                messages.error(
                    request, "We had a problem processing your card. {}".format(error['message'])
                )
                rollbar.report_exc_info(sys.exc_info(), request)
            except Exception as ex:
                if settings.DEBUG:
                    raise ex

                messages.error(
                    request, (
                        "We had a problem on our end processing your order. "
                        "You have not been charged. Our administrators have been notified."
                    )
                )
                rollbar.report_exc_info(sys.exc_info(), request)

    plan = {
        'stripe_id': subscription.plan.stripe_id,
        'amount': subscription.plan.amount,
        'display_price': subscription.plan.display_price(),
        'name': subscription.plan.name,
    }

    return render(
        request, "core/add_credit_card.html", {
            "subscription": subscription,
            "plan": plan,
            "plan_json": json.dumps(plan, cls=DjangoJSONEncoder),
            "email": request.user.email,
            "stripe_key": settings.STRIPE_PUBLISHABLE_KEY,
            "rebill_date": subscription.one_year_from_start().date(),
        }
    )
