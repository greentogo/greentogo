from django.contrib import admin
from django.contrib.auth.models import Group

import pinax.stripe.models as pinax_models

from .models import Location, Plan, Restaurant, Subscription, User


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


admin.site.register(User)
admin.site.register(Location, LocationAdmin)
admin.site.register(Restaurant)
admin.site.register(Subscription)
admin.site.register(Plan)

admin.site.unregister(Group)
admin.site.unregister(pinax_models.Charge)
admin.site.unregister(pinax_models.Customer)
admin.site.unregister(pinax_models.EventProcessingException)
admin.site.unregister(pinax_models.Event)
admin.site.unregister(pinax_models.Invoice)
admin.site.unregister(pinax_models.Plan)
admin.site.unregister(pinax_models.Transfer)
