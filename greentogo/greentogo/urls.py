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
from pinax.stripe.views import Webhook as StripeWebhook
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls

from beta_signup import views as beta_views
from core import views as core_views

urlpatterns = [
    url(r'^locations/(?P<location_code>[A-Za-z1-9]{6})/$', core_views.location, name='location'),
    url(r'^restaurants/$', core_views.restaurants, name='restaurants'),
    url(r'^account/subscription/new/$', core_views.add_subscription, name='add_subscription'),
    url(
        r'^account/subscription/(?P<sub_id>sub_[A-Za-z0-9]+)/$',
        core_views.subscription,
        name='subscription'
    ),
    url(
        r'^account/subscription/(?P<sub_id>sub_[A-Za-z0-9]+)/plan/$',
        core_views.change_subscription_plan,
        name='subscription_plan'
    ),
    url(
        r'^account/subscription/(?P<sub_id>sub_[A-Za-z0-9]+)/cancel/$',
        core_views.cancel_subscription,
        name='cancel_subscription'
    ),
    url(r'^account/change_password/$', core_views.change_password, name='change_password'),
    url(
        r'^account/change_payment_method/$',
        core_views.change_payment_method,
        name='change_payment_method'
    ),
    url(r'^account/$', core_views.account, name='account'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^auth/', include('djoser.urls.authtoken')),
    url(r'^webhook/', StripeWebhook.as_view(), name="pinax_stripe_webhook"),
    url(r'^beta-subscribe/$', beta_views.SubscriptionView.as_view(), name="beta-subscribe"),
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
