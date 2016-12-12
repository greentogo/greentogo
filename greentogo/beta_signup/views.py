from django.views.generic import View
from django.conf import settings
from django.shortcuts import render
from django import forms
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import stripe

from .models import Customer, Subscription, get_plan_price, add_plan_price

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_plans():
    plans = sorted(stripe.Plan.list()['data'], key=lambda p: p['amount'])
    return [add_plan_price(plan) for plan in plans]


def json_success(data):
    return JsonResponse({
        "status": "success",
        "data": data
    })


def json_error(message, data):
    return JsonResponse({
        "status": "error",
        "message": message,
        "data": data
    })


class SubscriptionForm(forms.Form):
    token = forms.CharField(max_length=100)
    name = forms.CharField(max_length=255)
    email = forms.CharField(max_length=255)
    plan = forms.CharField(max_length=100)


class SubscriptionView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        plans = get_plans()
        stripe_key = settings.STRIPE_PUBLISHABLE_KEY
        return render(request, 'subscription.html', {
            'plans': plans,
            'stripe_key': stripe_key
        })

    def post(self, request, *args, **kwargs):
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            plan = form.cleaned_data['plan']

            stripe_customer = stripe.Customer.create(
                email=email,
                source=form.cleaned_data['token'],
            )

            stripe_subscription = stripe.Subscription.create(
                customer=stripe_customer.id,
                plan=plan,
            )

            customer = Customer(stripe_id=stripe_customer.id,
                                name=name,
                                email=email)
            customer.save()
            if not customer.pk:
                return json_error(
                    "Could not create customer.",
                    {
                        "stripe_id": stripe_customer.id,
                        "name": customer.name,
                        "email": customer.email
                    }
                )

            subscription = Subscription(stripe_id=stripe_subscription.id,
                                        customer=customer,
                                        plan=plan)
            subscription.save()
            if not subscription.pk:
                return json_error(
                    "Could not create subscription.",
                    {
                        "stripe_id": subscription.stripe_id,
                        "plan": subscription.plan,
                    }
                )

            return json_success({
                "customer": {
                    "name": customer.name,
                    "email": customer.email,
                    "stripe_id": customer.stripe_id
                },
                "subscription": {
                    "plan": subscription.plan,
                    "stripe_id": subscription.stripe_id
                }
            })
        else:
            return json_error("Your form data was invalid.", form.cleaned_data)
