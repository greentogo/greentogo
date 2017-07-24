import csv

from django.contrib import admin
from django.contrib.auth.models import Group
from django.http import HttpResponse

from registration.models import RegistrationProfile
from rest_framework.authtoken.models import Token
from taggit.models import Tag
from wagtail.wagtailcore.models import Page, Site
from wagtail.wagtaildocs.models import Document
from wagtail.wagtailimages.models import Image

from .models import Location, Plan, Restaurant, Subscription, UnclaimedSubscription, User


class LocationAdmin(admin.ModelAdmin):
    fields = ('name', 'code', 'service', 'address', 'latitude', 'longitude', )
    readonly_fields = ('code', 'latitude', 'longitude', )
    list_display = ('name', 'code', 'service', )
    actions = [
        'make_qrcodes',
    ]

    def make_qrcodes(self, request, queryset):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from django.http import HttpResponse

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="qrcodes.pdf"'

        pdf = canvas.Canvas(response, letter)
        for location in queryset.all():
            location.add_qrcode_to_pdf(pdf)
        pdf.save()
        return response

    make_qrcodes.short_description = "Generate QR codes for selected locations"


@admin.site.register_view(
    'unclaimed_subscriptions.csv', name="Download CSV of claimed subscriptions"
)
def unclaimed_subscription_status_csv(request, *args, **kwargs):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="unclaimed_subscriptions.csv"'

    writer = csv.writer(response)
    writer.writerow(['Email address', 'Subscription plan', 'Claimed'])
    unsubs = UnclaimedSubscription.objects.all()
    for unsub in unsubs:
        writer.writerow([unsub.email, unsub.plan.name, unsub.claimed])

    return response


admin.site.register(User)
admin.site.register(Location, LocationAdmin)
admin.site.register(Restaurant)
admin.site.register(Subscription)
admin.site.register(Plan)
admin.site.register(UnclaimedSubscription)

admin.site.unregister(Group)
admin.site.unregister(Token)
admin.site.unregister(Tag)
admin.site.unregister(Document)
admin.site.unregister(RegistrationProfile)
admin.site.unregister(Image)
admin.site.unregister(Page)
admin.site.unregister(Site)
