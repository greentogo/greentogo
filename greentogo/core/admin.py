from django.contrib import admin
from django.http import HttpResponse

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

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="qrcodes.pdf"'

        pdf = canvas.Canvas(response, letter)
        for location in queryset.all():
            location.add_qrcode_to_pdf(pdf)
        pdf.save()
        return response

    make_qrcodes.short_description = "Generate QR codes for selected locations"
