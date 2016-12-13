from django.views.generic import View
from django.conf import settings
from django.shortcuts import render, redirect
from django import forms
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

import stripe

from .models import Customer, Subscription, get_plan_price, add_plan_price

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_plans():
    plans = sorted(stripe.Plan.list()['data'], key=lambda p: p['amount'])
    return [add_plan_price(plan) for plan in plans]


class SubscriptionForm(forms.Form):
    token = forms.CharField(max_length=100)
    name = forms.CharField(max_length=255)
    email = forms.CharField(max_length=255)
    plan = forms.CharField(max_length=100)
    gifted_to_name = forms.CharField(max_length=255, required=False)
    gifted_to_email = forms.CharField(max_length=255, required=False)


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
                return redirect(reverse('beta-error'))

            subscription = Subscription(stripe_id=stripe_subscription.id,
                                        customer=customer,
                                        plan=plan,
                                        gifted_to_name=form.cleaned_data[
                                            'gifted_to_name'],
                                        gifted_to_email=form.cleaned_data['gifted_to_email'])
            subscription.save()
            if not subscription.pk:
                return redirect(reverse('beta-error'))

            return redirect(reverse('beta-thanks'))
        else:
            return redirect(reverse('beta-error'))
