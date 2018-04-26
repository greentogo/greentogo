from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm

from registration.forms import RegistrationFormTermsOfService
from .models import Plan, Subscription

class UserSignupForm(RegistrationFormTermsOfService):
    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'email',
            'referred_by',
        ]

class UserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = [
            'name',
            'email',
        ]

    def clean_name(self):
        name = self.cleaned_data['name']
        if not name:
            self.add_error('name', 'You cannot leave your name blank.')

        return name


def available_plan_choices():
    return [
        (
            plan.id,
            "{name}: {display_price}".format(name=plan.name, display_price=plan.display_price()),
        ) for plan in Plan.objects.available()
    ]


class SubscriptionPlanForm(forms.Form):
    plan = forms.ChoiceField(choices=available_plan_choices)


# TODO use id instead of stripe id
def available_plan_choices_stripe_id():
    return [
        (plan.stripe_id, "{}: {}".format(plan.name, plan.display_price()), )
        for plan in Plan.objects.available()
    ]


class NewSubscriptionForm(forms.Form):
    token = forms.CharField(max_length=100, widget=forms.HiddenInput)
    plan = forms.ChoiceField(choices=available_plan_choices_stripe_id)
    coupon_code = forms.CharField(max_length=20, required=False, label="Corporate access code")


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = [
            'name',
        ]

class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not get_user_model().objects.filter(email__iexact=email, is_active=True).exists():
            self.add_error('email', 'There is no user registered with the specified email address.')
        return email
