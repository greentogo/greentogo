from django import forms
from django.contrib.auth import get_user_model

from .models import Plan, Subscription


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


class SubscriptionPlanForm(forms.Form):
    plan = forms.ChoiceField(
        choices=[
            (
                plan.id, "{name}: {display_price}".format(
                    name=plan.name, display_price=plan.display_price()
                ),
            ) for plan in Plan.objects.available()
        ]
    )


class NewSubscriptionForm(forms.Form):
    token = forms.CharField(max_length=100, widget=forms.HiddenInput)
    plan = forms.ChoiceField(
        choices=[
            (plan.stripe_id, "{}: {}".format(plan.name, plan.display_price()), )
            for plan in Plan.objects.available()
        ]
    )


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = [
            'name',
        ]
