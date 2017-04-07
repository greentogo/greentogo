from django.contrib import admin

from .models import Location, Restaurant, Subscriber, Subscription, User


class LinkedSubscriptionInline(admin.StackedInline):
    model = Subscriber.subscriptions.through


class SubscriberAdmin(admin.ModelAdmin):
    inlines = [
        LinkedSubscriptionInline,
    ]
    fields = ('user', )
    list_display = ('username', )


class LocationAdmin(admin.ModelAdmin):
    fields = ('name', 'code', 'service', 'address', 'latitude', 'longitude', )
    readonly_fields = ('code', 'latitude', 'longitude', )
    list_display = ('name', 'code', 'service', )


admin.site.register(User)
admin.site.register(Location, LocationAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Restaurant)
