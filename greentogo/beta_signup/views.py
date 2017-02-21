from django.views.generic import View
from django.conf import settings
from django.shortcuts import render, redirect
from django import forms
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from django.contrib.auth import get_user_model

import stripe
from pinax.stripe.models import Plan
from pinax.stripe.actions import invoices, customers, subscriptions

from .models import get_plans, send_subscriber_email, send_admin_email, GiftSubscription

User = get_user_model()

stripe.api_key = settings.STRIPE_SECRET_KEY


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
        return render(request, 'subscription.html',
                      {'plans': plans,
                       'stripe_key': stripe_key})

    def post(self, request, *args, **kwargs):
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            plan = form.cleaned_data['plan']
            token = form.cleaned_data['token']

            try:
                user = User.objects.get(email=email)
                user.name = name
                user.save()
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=email, email=email, name=name)

            customer = customers.get_customer_for_user(user)
            if customer is None:
                customer = customers.create(user)

            subscription = subscriptions.create(
                customer, plan=plan, token=token)

            if form.cleaned_data['gifted_to_name']:
                gift = GiftSubscription(
                    stripe_subscription=subscription,
                    gifted_to_name=form.cleaned_data['gifted_to_name'],
                    gifted_to_email=form.cleaned_data['gifted_to_email'], )
                gift.save()

            send_subscriber_email(subscription)
            send_admin_email(subscription)

            return redirect(reverse('beta-thanks'))
        else:
            return redirect(reverse('beta-error'))
