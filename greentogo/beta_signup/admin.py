from django.contrib import admin

from .models import Customer, Subscription

admin.site.register(Customer)
admin.site.register(Subscription)
