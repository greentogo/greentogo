import inspect

from django.contrib import admin
from django.views.generic import View

from django.contrib.auth.models import Group

from core.admin import LocationAdmin, UnclaimedSubscriptionAdmin, GroupAdmin,\
                        SubscriptionAdmin, PlanAdmin, CustomUserAdmin
from core.models import (
    CorporateCode, Location, LocationTag, Plan, Restaurant, Subscription, UnclaimedSubscription,
    User, CouponCode, LocationStockReport
)
from core.views.admin import (
    activity_report, empty_location, empty_locations, restock_location, restock_locations,
    stock_report, export_data, unclaimed_subscription_status_csv, export_total_check_out, 
    export_total_check_in, export_check_out_by_user, export_check_in_by_user, 
)

from export_action.admin import export_selected_objects


def is_class_based_view(view):
    return inspect.isclass(view) and issubclass(view, View)


class G2GAdminSite(admin.AdminSite):
    index_template = 'admin/dashboard.html'
    site_header = 'Durham GreenToGo Admin'

    def __init__(self, *args, **kwargs):
        self.custom_sections = {}
        return super().__init__(*args, **kwargs)

    def register_view(
        self, path, name=None, section="Custom Views", urlname=None, \
        visible=True, view=None, only_superusers=False
    ):
        """Add a custom admin view. Can be used as a function or a decorator.
        * `path` is the path in the admin where the view will live, e.g.
            http://example.com/admin/somepath
        * `name` is an optional pretty name for the list of custom views. If
            empty, we'll guess based on view.__name__.
        * `section` is the header for the section this will appear in
        * `urlname` is an optional parameter to be able to call the view with a
            redirect() or reverse()
        * `visible` is a boolean or predicate returning one, to set if
            the custom view should be visible in the admin dashboard or not.
        * `view` is any view function you can imagine.
        """

        def decorator(fn):
            if is_class_based_view(fn):
                fn = fn.as_view()
            if section not in self.custom_sections:
                self.custom_sections[section] = []

            self.custom_sections[section].append((path, fn, name, urlname, visible, only_superusers))
            return fn

        if view is not None:
            decorator(view)
            return
        return decorator

    def get_urls(self):
        """Add our custom views to the admin urlconf."""
        urls = super().get_urls()
        from django.conf.urls import url
        for section, views in self.custom_sections.items():
            for path, view, name, urlname, visible, only_superusers in views:
                urls = [
                    url(r'^%s$' % path, self.admin_view(view), name=urlname),
                ] + urls
        return urls

    def index(self, request, extra_context=None):
        """Make sure our list of custom views is on the index page."""
        if not extra_context:
            extra_context = {}
        custom_list = {}


        for section, views in self.custom_sections.items():
            custom_list[section] = []
            for path, view, name, urlname, visible, only_superusers in views:
                if only_superusers and not request.user.is_superuser:
                    #only add superuser views if the user is a superuser
                    continue

                if callable(visible):
                    visible = visible(request)
                if visible:
                    if name:
                        custom_list[section].append((path, name))
                    else:
                        custom_list[section].append((path, view.__name__))

            if custom_list[section] == []:
                #the user has no permissions to edit anything in this section
                #remove empty section
                custom_list.pop(section, None)

        # Sort views alphabetically.
        # custom_list.sort(key=lambda x: x[1])

        extra_context.update({'custom_sections': custom_list})
        return super().index(request, extra_context)


admin_site = G2GAdminSite(name='greentogo')
admin_site.site_header = 'GreenToGo Admin'
admin_site.site_title = 'GreenToGo Admin'

admin_site.register_view(
    path='core/unclaimed_subscriptions.csv',
    view=unclaimed_subscription_status_csv,
    section="Reports",
    name="Download CSV of claimed subscriptions",
    only_superusers=True,
)

admin_site.register_view(
    path='export_data/core/export_total_check_out.csv',
    view=export_total_check_out,
    name="Download CSV",
    only_superusers=True,
)

admin_site.register_view(
    path='export_data/core/export_total_check_in.csv',
    view=export_total_check_in,
    name="Download CSV",
    only_superusers=True,
)

admin_site.register_view(
    path='export_data/core/export_check_out_by_user.csv',
    view=export_check_out_by_user,
    name="Download CSV",
    only_superusers=True,
)

admin_site.register_view(
    path='export_data/core/export_check_in_by_user.csv',
    view=export_check_in_by_user,
    name="Download CSV",
    only_superusers=True,
)

# admin_site.register_view(
#     path='restock_locations/',
#     view=restock_locations,
#     section="Stock Management",
#     name="Restock checkout locations",
#     urlname="restock_locations",
# )
#
# admin_site.register_view(
#     path='restock_locations/(?P<location_id>[0-9]+)/',
#     view=restock_location,
#     section="Stock Management",
#     visible=False,
#     urlname="restock_location",
# )
#
# admin_site.register_view(
#     path='empty_locations/',
#     view=empty_locations,
#     section="Stock Management",
#     name="Empty checkin locations",
#     urlname="empty_locations",
# )
#
# admin_site.register_view(
#     path='empty_locations/(?P<location_id>[0-9]+)/',
#     view=empty_location,
#     section="Stock Management",
#     visible=False,
#     urlname="empty_location",
# )

admin_site.register_view(
    path='stock_report/',
    view=stock_report,
    section="Reports",
    name="Location Stock Report",
    urlname="stock_report",
    only_superusers=True,
)

admin_site.register_view(
    path='activity_report/',
    view=activity_report,
    section="Reports",
    name="Activity Report",
    urlname="activity_report",
    only_superusers=True,
)

admin_site.register_view(
    path='export_data/',
    view=export_data,
    section="Reports",
    name="Export Data",
    urlname="export_data",
    only_superusers=True,
)

admin_site.register(Group, GroupAdmin)

admin_site.register(User, CustomUserAdmin)
admin_site.register(Location, LocationAdmin)
admin_site.register(Restaurant)
admin_site.register(Subscription, SubscriptionAdmin)
admin_site.register(Plan, PlanAdmin)
admin_site.register(UnclaimedSubscription, UnclaimedSubscriptionAdmin)
admin_site.register(CorporateCode)
admin_site.register(CouponCode)
admin_site.register(LocationTag)
admin_site.register(LocationStockReport)


# export tools
# all export-able models need to be registered with the default admin.site
# note: register with admin.site, not admin_site (which is our G2GAdminSite)
admin.site.register(User)
admin.site.register(Location)
admin.site.register(Restaurant)
admin.site.register(Subscription)
admin.site.register(Plan)
admin.site.register(UnclaimedSubscription)
admin.site.register(CorporateCode)
admin.site.register(CouponCode)
admin.site.register(LocationTag)
admin.site.register(LocationStockReport)

#Add the export action to the custom admin site
admin_site.add_action(export_selected_objects)
