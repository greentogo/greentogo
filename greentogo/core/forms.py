from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm

from registration.forms import RegistrationFormTermsOfService
from .models import Plan, Subscription, Location

# import datetime
from datetime import date, timedelta, datetime

class UserSignupForm(RegistrationFormTermsOfService):
    email2 = forms.EmailField()
    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'email',
            'referred_by',
        ]
    def clean(self):
        cleaned_data = super(UserSignupForm, self).clean()
        email = cleaned_data.get('email')
        email2 = cleaned_data.get('email2')

        if email and email2 and email != email2:
            self._errors['email2'] = self.error_class(['Emails do not match.'])
        return cleaned_data

class ExportForm(forms.Form):
    from_date = forms.DateField(label='From Date', initial=datetime.now() - timedelta(days=30), input_formats=['%Y-%m-%d'])
    to_date = forms.DateField(label='To Date', initial=datetime.now(), input_formats=['%Y-%m-%d'])
    class Meta:
        fields = [
                'from_date',
                'to_date',
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

class AccidentalCheckoutForm(forms.Form):
    num_boxes = forms.IntegerField(min_value=0, max_value=4)
    location = forms.ModelChoiceField(queryset=Location.objects.filter(service="OUT", admin_location=False, retired=False))
    def clean_num_boxes(self):
        data = self.cleaned_data['num_boxes']
        return data