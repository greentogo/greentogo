from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse
from django.utils.html import format_html
from django.conf.urls import include, url
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, resolve
from django.shortcuts import get_object_or_404, redirect, render
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter
from django.contrib.admin import SimpleListFilter
from django.utils import timezone

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
            for i in range(sub.boxes_currently_out()):
                # Use the first admin Location, failing that use first location
                checkin_location = Location.objects.filter(admin_location=True).first() \
                    or Location.objects.checkin().first()
                LocationTag.objects.create(subscription=sub, location=checkin_location)


checkin_all_boxes.short_description = "Return all boxes for selected users"

class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0
    fields = ('inline_display_name','plan', 'stripe_id', 'boxes_currently_out', 'available_boxes', 'max_boxes', )
    readonly_fields = ('inline_display_name', 'plan', 'stripe_id', 'boxes_currently_out', 'available_boxes', 'max_boxes', )
    can_delete = False
    view_on_site = False
    show_change_link = True
    
    def inline_display_name(self,obj):
        return obj.display_name

    def has_add_permission(self, request):
        return False

class RestaurantManagerInline(admin.TabularInline):
    model = User.restaurant_manager.through

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'reward_points', 'is_staff', )
    inlines = [SubscriptionInline,RestaurantManagerInline]

class isActiveFilter(SimpleListFilter):
    title = 'Active'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('Active', 'Active'),
            ('Inactive', 'Inactive'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Active':
            return queryset.filter(ends_at__gte=timezone.now().date()) | queryset.filter(ends_at=None)
        if self.value() == 'Inactive':
            return queryset.filter(ends_at__lte=timezone.now().date())

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('stripe_id', 'user', 'plan', 'boxes_currently_out', 'available_boxes', 'max_boxes', 'is_active', )
    search_fields = ('name', 'user__name', 'user__username', 'stripe_id', )
    readonly_fields = ('boxes_currently_out', 'available_boxes', 'max_boxes', 'last_used', 'total_checkins', 'total_checkouts', 'is_active', 'account_actions', )
    list_filter = (
        isActiveFilter,
        # for ordinary fields
        # ('stripe_status', DropdownFilter),
        # for related fields
        # ('user__name', RelatedDropdownFilter),
    )

    def admin_checkin(self, request, account_id, *args, **kwargs):
        return self.process_action(
            request=request,
            account_id=account_id,
            action='IN',
        )
    def admin_checkout(self, request, account_id, *args, **kwargs):
        return self.process_action(
            request=request,
            account_id=account_id,
            action='OUT',
        )

    def process_action(
        self,
        request,
        account_id,
        action
    ):
        subscription = Subscription.objects.get(id=account_id)
        try:
            dump = Location.objects.get(dumping_location=True, service=action)
            if subscription.can_tag_location(dump):
                subscription.tag_location(dump, 1)
            else:
                messages.add_message(request, messages.WARN, 'Unable to check {} box. user has no boxes left to check {}'.format(action, action))
        except Location.DoesNotExist:
            messages.add_message(request, messages.ERROR, 'No Check{} Dumping Location has been set! Please create a check{} dumping location'.format(action, action))
        except:
            messages.add_message(request, messages.ERROR, 'ERROR: Unable to process')
        return redirect('admin:core_subscription_change', account_id)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<account_id>.+)/adminCheckin/$',
                self.admin_site.admin_view(self.admin_checkin),
                name='admin-checkin',
            ),
            url(
                r'^(?P<account_id>.+)/adminCheckout/$',
                self.admin_site.admin_view(self.admin_checkout),
                name='admin-checkout',
            ),
        ]
        return custom_urls + urls

    actions = [checkin_all_boxes]
    def account_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">CheckIn</a>&nbsp;'
            '<a class="button" href="{}">CheckOut</a>',
            reverse('admin:admin-checkin', args=(obj.id,)),
            reverse('admin:admin-checkout', args=(obj.id,)),
        )
    account_actions.short_description = 'Account Actions'


class PlanAdmin(admin.ModelAdmin):
    ordering = ('-available',)

class UnclaimedSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'plan', 'claimed', )
    search_fields = ('email', )


class LocationAdmin(admin.ModelAdmin):
    fields = ('name', 'code', 'service', 'address', 'website', 'latitude', 'longitude', 'minimum_boxes', 'phase', 'admin_location', 'headquarters', 'washing_location', 'dumping_location', 'notify', 'notifyEmail', 'retired', 'error_rate', 'avg_weekly_usage_over_past_4_weeks', 'neighborhood', 'dashboard', )
    readonly_fields = ('code', 'latitude', 'longitude', 'is_admin_location', 'error_rate', 'avg_weekly_usage_over_past_4_weeks', 'dashboard', )
    list_display = ('name', 'code', 'service', 'is_admin_location', )
    actions = [
        'make_qrcodes',
    ]
    inlines = [RestaurantManagerInline]

    def dashboard(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.dashboard_url)

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
