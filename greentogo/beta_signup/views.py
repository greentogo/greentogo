from django.shortcuts import render
from django.views.generic import TemplateView

from .models import Plan


class SubscriptionView(TemplateView):
    template_name = "subscription.html"

    def get_context_data(self, **kwargs):
        context = super(SubscriptionView, self).get_context_data(**kwargs)
        context['plans'] = Plan.objects.order_by('name')
        return context
