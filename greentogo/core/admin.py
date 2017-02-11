from django.contrib import admin
from .models import User, Subscriber, Subscription, SubscriptionPlan, Location


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
    model = Subscriber.subscriptions.through


class SubscriberAdmin(admin.ModelAdmin):
    inlines = [LinkedSubscriptionInline, OwnedSubscriptionInline]
    fields = ('user', )
    list_display = ('username', )


admin.site.register(User)
admin.site.register(Location)
admin.site.register(SubscriptionPlan)
admin.site.register(Subscriber, SubscriberAdmin)
