from django.contrib import admin
from .models import EmailAddress, Customer, Subscription, SubscriptionPlan, Location


class EmailAddressInline(admin.TabularInline):
    model = EmailAddress


class OwnedSubscriptionInline(admin.TabularInline):
    model = Subscription
    verbose_name = "Owned Subscription"
    verbose_name_plural = "Owned Subscriptions"

    fields = (
        'plan',
        'started_on',
        'expires_on',
        'stripe_id', )


class LinkedSubscriptionInline(admin.StackedInline):
    model = Customer.subscriptions.through


class CustomerAdmin(admin.ModelAdmin):
    inlines = [
        EmailAddressInline, LinkedSubscriptionInline, OwnedSubscriptionInline
    ]
    fields = ('name', )
    list_display = ('name', )


admin.site.register(Location)
admin.site.register(SubscriptionPlan)
admin.site.register(Customer, CustomerAdmin)
