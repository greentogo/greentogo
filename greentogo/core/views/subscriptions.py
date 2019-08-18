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
from core.models import CorporateCode, CouponCode, Plan, Subscription, User
from core.utils import decode_id, encode_nums

rollbar.init(settings.ROLLBAR_KEY, settings.ROLLBAR_ENV)


class CouponExpired(Exception):
   """Raised when the coupon is expired"""
   pass

@login_required
def subscriptions_view(request):
    user = request.user
    if not user.stripe_id:
        user.create_stripe_customer()
    # subscriptions = request.user.subscriptions.active().order_by("starts_at")
    return render(request, 'core/subscriptions.html')


@login_required
def add_subscription(request, code=False, *args, **kwargs):
    user = request.user
    if not user.stripe_id:
        user.create_stripe_customer()
    corporate_code = None
    coupon_code = None
    if code:
        try:
            coupon_code = CouponCode.objects.get(code=code)
            if coupon_code.redeem_by < datetime.now().date():
                messages.error(request, "That coupon has expired")
                return redirect('/subscriptions/new/')
        except CouponCode.DoesNotExist:
            coupon_code = None
        try:
            corporate_code = CorporateCode.objects.get(code=code)
            if corporate_code.redeem_by < datetime.now().date():
                messages.error(request, "That corporate code has expired")
                return redirect('/subscriptions/new/')
        except CorporateCode.DoesNotExist:
            corporate_code = None
    if 'code' in kwargs and 'coupon_type' in kwargs:
        if kwargs['coupon_type'] == 'corporate':
            corporate_code = get_object_or_404(CorporateCode, code=kwargs['code'])
        else:
            coupon_code = get_object_or_404(CouponCode, code=kwargs['code'])

    if request.method == "POST":
        
        if 'couponCode' in request.POST:
            try:
                coupon = CouponCode.objects.get(code=request.POST['code'])
                #fail if the users email is not allowed by the coupon
                if coupon.emails and request.user.email not in coupon.emails:
                    raise Exception
                #fail if none of the coupons plans are available
                if coupon.plans.count() > 0 and not any([p.available for p in
                    coupon.plans.all()]):
                    raise Exception
                #fail if there is a subscription with this coupon already attached
                #to the user 
                if request.user.subscriptions.filter(coupon_code=coupon).count() == 0:
                    redirURL = "/subscriptions/new/{}/".format(coupon.code)
                    return redirect(redirURL)
                else:
                    messages.error(request, "You have already used that coupon.")
            except CouponCode.DoesNotExist:
                messages.error(request, "That is not a valid coupon.")
            except Exception as ex:
                messages.error(request, "Error: That is not a valid coupon.")
                rollbar.report_exc_info(sys.exc_info(), request)

        else:
            form = NewSubscriptionForm(request.POST)
            if form.is_valid():

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
                elif coupon_code:
                    sub_kwargs['coupon'] = coupon_code.code


                try:
                    if corporate_code:
                        sub_kwargs['billing'] = 'send_invoice'
                        sub_kwargs['days_until_due'] = 30
                    # sub_kwargs
                    # {'customer': 'cus_Ck3yEqbljkn0Zp', 'source': 'tok_1CszGPDR4unvi416aLuq8bR5', 'items': [{'plan': '4-boxesC9MB77'}]}
                    stripe_subscription = stripe.Subscription.create(**sub_kwargs)
                    subscription = Subscription.create_from_stripe_sub(
                        user=user,
                        plan=plan,
                        stripe_subscription=stripe_subscription,
                        corporate_code=corporate_code,
                        coupon_code=coupon_code
                    )
                    #'cancel' the subscription, so that the corporate plans do not auto renew
                    # if corporate_code:
                    #     stripe_sub = subscription.get_stripe_subscription()
                    #     stripe_sub.delete(at_period_end = True)
                    #     subscription.cancelled = True
                    #     subscription.save()
                    return redirect('/subscriptions/')
                except stripe.error.CardError as ex:
                    print(ex)
                    error = ex.json_body.get('error')
                    messages.error(
                        request, "We had a problem processing your card. {}".format(error['message'])
                    )
                    rollbar.report_exc_info(sys.exc_info(), request)
                except Exception as ex:
                    print(ex)
                    messages.error(
                        request, (
                            "We had a problem on our end processing your order. "
                            "You have not been charged. Our administrators have been notified."
                        )
                    )
                    rollbar.report_exc_info(sys.exc_info(), request)

    available_plans = Plan.objects.available().order_by('name')
    if coupon_code and coupon_code.plans.count() > 0:
        available_plans = coupon_code.plans.all()

    plans = [
        {
            'stripe_id': plan.stripe_id,
            'amount': plan.amount,
            'display_price': plan.display_price(
                corporate_code = corporate_code,
                coupon_code = coupon_code
            ),
            'name': plan.name,
        } for plan in available_plans 
    ]

    plandict = {plan['stripe_id']: plan for plan in plans}

    return render(
        request, "core/add_subscription.html", {
            "form": NewSubscriptionForm(),
            "corporate_code": corporate_code,
            "coupon_code": coupon_code,
            "plans": plans,
            "plandict_json": json.dumps(plandict, cls=DjangoJSONEncoder),
            "email": request.user.email,
            "stripe_key": settings.STRIPE_PUBLISHABLE_KEY
        }
    )

@login_required
def renew_corporate(request, sub_id):
    real_id = decode_id(sub_id)[0]
    user = request.user
    subscription = user.subscriptions.get(id=real_id)
    if request.method == "POST":
        try:
            code = CorporateCode.objects.get(code=request.POST['code'])
            if request.user.subscriptions.filter(corporate_code=code).count() == 0:
                subscription.corporate_code = code
                subscription.cancelled = False
                subscription.save()
                stripeSub = stripe.Subscription.retrieve(subscription.stripe_id)
                stripeSub.coupon = code.code
                stripeSub.cancel_at_period_end = False
                stripeSub.save()
                messages.add_message(request, messages.INFO, "Successfully renewed corporate subscription!")
                return redirect('/subscriptions/')
            else:
                messages.error(request, "You have already used that corporate access code.")
        except CorporateCode.DoesNotExist:
            messages.error(request, "That is not a valid corporate access code.")
    return render(request, "core/renew_corporate.html")

@login_required
def coupon_subscription(request, *args, **kwargs):
    # TODO CURRENTLY UNUSED, ALTHOUGH THE URL STILL EXISTS
    """Check coupon code to see if valid."""
    if request.method == "POST":
        try:
            coupon = CouponCode.objects.get(code=request.POST['code'])
            #fail if the users email is not allowed by the coupon
            if coupon.emails and request.user.email not in coupon.emails:
                raise Exception
            #fail if none of the coupons plans are available
            if coupon.plans.count() > 0 and not any([p.available for p in
                coupon.plans.all()]):
                raise Exception
            #fail if there is a subscription with this coupon already attached
            #to the user 
            if request.user.subscriptions.filter(coupon_code=coupon).count() == 0:
                return redirect(reverse('add_coupon_subscription',
                    kwargs={'code': coupon.code, 'coupon_type':'coupon'}))
            else:
                messages.error(request, "You have already used that coupon.")
        except CouponCode.DoesNotExist:
            messages.error(request, "That is not a valid coupon.")
        except:
            messages.error(request, "That is not a valid coupon.")

    return render(request, "core/coupon_subscription.html")

@login_required
def corporate_subscription(request, *args, **kwargs):
    """Check corporate code to see if valid."""
    if request.method == "POST":
        try:
            code = CorporateCode.objects.get(code=request.POST['code'])
            if request.user.subscriptions.filter(corporate_code=code).count() == 0:
                return redirect(reverse('add_corporate_subscription',
                    kwargs={'code': code.code,'coupon_type':'corporate'}))
            else:
                messages.error(request, "You have already used that corporate access code.")
        except CorporateCode.DoesNotExist:
            messages.error(request, "That is not a valid corporate access code.")

    return render(request, "core/corporate_subscription.html")


@login_required
def cancel_subscription(request, sub_id):
    real_id = decode_id(sub_id)[0]
    user = request.user
    subscription = user.subscriptions.get(id=real_id)
    if request.method == "POST":
        #cancel the subscription
        subscription.cancelled = True
        subscription.save()

        cancel_message = """
We’re sorry to see you go! If you have feedback for our team that could help us improve this service (and keep you enrolled!), please don’t hesitate to contact us at info@durhamgreentogo.com. We always read our customer emails and will respond to your concerns! 
        """

        messages.success(request, cancel_message)
        return redirect(reverse('subscriptions'))

    return render(
        request, "core/cancel_subscription.html", {
            "subscription": subscription,
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
                subscription.sync_with_stripe(stripe_subscription)

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
