from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse

from .models import Location, UnclaimedSubscription, Subscription, LocationTag,\
        User

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
                # Use the first admin Location, failing that use first location
                checkin_location = Location.objects.filter(admin_location=True).first() \
                    or Location.objects.checkin().first()
                LocationTag.objects.create(subscription=sub, location=checkin_location)


checkin_all_boxes.short_description = "Return all boxes for selected users"

class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0
    fields = ('inline_display_name','plan', 'stripe_id')
    readonly_fields = ('inline_display_name', 'plan', 'stripe_id')
    can_delete = False
    view_on_site = False
    show_change_link = True
    
    def inline_display_name(self,obj):
        return obj.display_name

    def has_add_permission(self, request):
        return False

class CustomUserAdmin(UserAdmin):
    inlines = [SubscriptionInline,]

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('stripe_id', 'user', 'plan', 'boxes_checked_out', 'available_boxes', 'max_boxes', )
    search_fields = ('name', 'user__name', 'user__username', 'stripe_id', )
    readonly_fields = ('boxes_checked_out', 'available_boxes', 'max_boxes', )

    actions = [checkin_all_boxes]


class PlanAdmin(admin.ModelAdmin):
    ordering = ('-available',)

class UnclaimedSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'plan', 'claimed', )
    search_fields = ('email', )


class LocationAdmin(admin.ModelAdmin):
    fields = ('name', 'code', 'service', 'address', 'website', 'latitude', 'longitude', 'phase', 'admin_location', 'headquarters', 'washing_location', 'dumping_location', 'notify', 'notifyEmail', 'retired')
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

class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('permissions',)
