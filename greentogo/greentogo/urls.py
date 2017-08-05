"""greentogo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from adminplus.sites import AdminSitePlus
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls

import core.views.locations
import core.views.subscriptions
from core import views as core_views
from core.views.webhook import stripe_webhook

admin.site = AdminSitePlus()
admin.autodiscover()

urlpatterns = [
    url(r'^webhook/$', stripe_webhook),
    url(r'^locations/$', core.views.locations.locations, name='locations'),
    url(
        r'^locations/(?P<location_code>[A-Za-z1-9]{6})/$',
        core.views.locations.location,
        name='location'
    ),
    url(r'^restaurants/$', core_views.restaurants, name='restaurants'),
    url(r'^subscriptions/$', core.views.subscriptions.subscriptions_view, name='subscriptions'),
    url(
        r'^subscriptions/new/$', core.views.subscriptions.add_subscription, name='add_subscription'
    ),
    url(
        r'^subscriptions/(?P<sub_id>[A-Za-z0-9]+)/plan/$',
        core.views.subscriptions.change_subscription_plan,
        name='subscription_plan'
    ),
    url(r'^account/change_password/$', core_views.change_password, name='change_password'),
    url(
        r'^account/change_payment_method/$',
        core_views.change_payment_method,
        name='change_payment_method'
    ),
    url(r'^account/$', core_views.account_settings, name='account_settings'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^auth/', include('djoser.urls.authtoken')),
    url(r'^thanks/', TemplateView.as_view(template_name="thanks.html"), name="beta-thanks"),
    url(r'^error/', TemplateView.as_view(template_name="error.html"), name="beta-error"),
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/', include('apiv1.urls')),
    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'', include(wagtail_urls)),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
