from django.contrib import admin

from .models import Plan, Customer, Subscription

admin.site.register(Plan)
admin.site.register(Customer)
admin.site.register(Subscription)
