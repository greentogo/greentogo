from django.contrib import admin
from django.http import HttpResponse

from .models import Location, UnclaimedSubscription, Subscription, LocationTag

def checkin_all_boxes(modeladmin, request, queryset):
    """
    Box count is tied to the subscription model, but we
    want to operate on users. This function should find
    the related subscription and perform enough check-ins
    to reset all their boxes.
    """

    for sub in queryset:
        #Check if subscription can check in at least 1 box
        if sub.can_checkin():
            #Create checkin tags equal to number of boxes currently checked out
            for i in range(sub.boxes_checked_out()):
                # Use the first checkin LocationTag
                # TODO: determine best method for choosing checkin location
                LocationTag.objects.create(subscription=sub, location=Location.objects.checkin().first())


checkin_all_boxes.short_description = "Return all boxes for selected users"

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'plan', 'stripe_id', )
    search_fields = ('name', 'user__name', 'user__username', 'stripe_id', )

    actions = [checkin_all_boxes]

class UnclaimedSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'plan', 'claimed', )
    search_fields = ('email', )


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

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="qrcodes.pdf"'

        pdf = canvas.Canvas(response, letter)
        for location in queryset.all():
            location.add_qrcode_to_pdf(pdf)
        pdf.save()
        return response

    make_qrcodes.short_description = "Generate QR codes for selected locations"
