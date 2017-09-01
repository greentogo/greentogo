import inspect

from django.contrib import admin
from django.views.generic import View

from core.admin import LocationAdmin, UnclaimedSubscriptionAdmin
from core.models import (
    CorporateCode, Location, LocationTag, Plan, Restaurant, Subscription, UnclaimedSubscription,
    User
)
from core.views.admin import (
    activity_report, empty_location, empty_locations, restock_location, restock_locations,
    stock_report, unclaimed_subscription_status_csv
)


def is_class_based_view(view):
    return inspect.isclass(view) and issubclass(view, View)


class G2GAdminSite(admin.AdminSite):
    index_template = 'admin/dashboard.html'
    site_header = 'Durham GreenToGo Admin'

    def __init__(self, *args, **kwargs):
        self.custom_sections = {}
        return super().__init__(*args, **kwargs)

    def register_view(
        self, path, name=None, section="Custom Views", urlname=None, visible=True, view=None
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

            self.custom_sections[section].append((path, fn, name, urlname, visible, ))
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
            for path, view, name, urlname, visible in views:
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
            for path, view, name, urlname, visible in views:
                if callable(visible):
                    visible = visible(request)
                if visible:
                    if name:
                        custom_list[section].append((path, name))
                    else:
                        custom_list[section].append((path, view.__name__))

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
    name="Download CSV of claimed subscriptions"
)

admin_site.register_view(
    path='restock_locations/',
    view=restock_locations,
    section="Stock Management",
    name="Restock checkout locations",
    urlname="restock_locations",
)

admin_site.register_view(
    path='restock_locations/(?P<location_id>[0-9]+)/',
    view=restock_location,
    section="Stock Management",
    visible=False,
    urlname="restock_location",
)

admin_site.register_view(
    path='empty_locations/',
    view=empty_locations,
    section="Stock Management",
    name="Empty checkin locations",
    urlname="empty_locations",
)

admin_site.register_view(
    path='empty_locations/(?P<location_id>[0-9]+)/',
    view=empty_location,
    section="Stock Management",
    visible=False,
    urlname="empty_location",
)

admin_site.register_view(
    path='stock_report/',
    view=stock_report,
    section="Reports",
    name="Location Stock Report",
    urlname="stock_report",
)

admin_site.register_view(
    path='activity_report/',
    view=activity_report,
    section="Reports",
    name="Activity Report",
    urlname="activity_report",
)

admin_site.register(User)
admin_site.register(Location, LocationAdmin)
admin_site.register(Restaurant)
admin_site.register(Subscription)
admin_site.register(Plan)
admin_site.register(UnclaimedSubscription, UnclaimedSubscriptionAdmin)
admin_site.register(CorporateCode)
admin_site.register(LocationTag)
