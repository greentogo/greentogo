from django import forms

from .models import get_plans


class SubscriptionPlanForm(forms.Form):
    plan = forms.ChoiceField(
        choices=[
            (plan['stripe_id'], "{name}: {display_price}".format(**plan), ) for plan in get_plans()
        ]
    )
