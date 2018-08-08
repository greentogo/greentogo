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
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from rest_framework.documentation import include_docs_urls

import core.views.locations
import core.views.subscriptions
import core.views.reporting
import core.views.registration
from core import views as core_views
from core.views.webhook import stripe_webhook

from core.forms import EmailValidationOnForgotPassword

from .adminsite import admin_site

subscriptions_patterns = [
    url(r'^$', core.views.subscriptions.subscriptions_view, name='subscriptions'),
    url(
        r'^corporate/$',
        core.views.subscriptions.corporate_subscription,
        name='corporate_subscription'
    ),
        url(
        r'^renew_corporate/$',
        core.views.subscriptions.renew_corporate,
        name='renew_corporate'
    ),
    url(
        r'^coupon/$',
        core.views.subscriptions.coupon_subscription,
        name='coupon_subscription'
    ),
    url(r'^new/$', core.views.subscriptions.add_subscription, name='add_subscription'),
    url(r'^new/(?P<code>[A-Z0-9]+)/$', core.views.subscriptions.add_subscription, name='add_subscription'),
    url(
        r'^new/(?P<coupon_type>corporate)/(?P<code>[A-Z0-9]+)/$',
        core.views.subscriptions.add_subscription,
        name='add_corporate_subscription'
    ),
    url(
        r'^new/(?P<coupon_type>coupon)/(?P<code>[A-Z0-9]+)/$',
        core.views.subscriptions.add_subscription,
        name='add_coupon_subscription'
    ),
    url(
        r'^(?P<sub_id>[A-Za-z0-9]+)/plan/$',
        core.views.subscriptions.change_subscription_plan,
        name='subscription_plan'
    ),
    url(
        r'^(?P<sub_id>[A-Za-z0-9]+)/add_cc/$',
        core.views.subscriptions.add_credit_card,
        name='subscription_add_credit_card',
    ),
    url(
        r'^(?P<sub_id>[A-Za-z0-9]+)/cancel/$',
        core.views.subscriptions.cancel_subscription,
        name='cancel_subscription',
    ),
]

urlpatterns = [
    url(r'^webhook/$', stripe_webhook),
    url(r'^locations/$', core.views.locations.locations, name='locations'),
    url(
        r'^locations/(?P<location_code>[A-Za-z1-9]{6})/$',
        core.views.locations.location,
        name='location'
    ),
    url(r'^restaurants/$', core_views.restaurants, name='restaurants'),
    url(r'^subscriptions/', include(subscriptions_patterns)),
    url(r'^account/change_password/$', core_views.change_password, name='change_password'),
    url(
        r'^account/change_payment_method/$',
        core_views.change_payment_method,
        name='change_payment_method'
    ),
    url(r'^export_action/', include("export_action.urls", namespace="export_action")),
    url(r'^account/$', core_views.account_settings, name='account_settings'),

    #catch password reset to use our own form
    url(r'^accounts/register/', core.views.registration.registration_form),
    url(r'^accounts/password/reset/$',  auth_views.password_reset,
    {'post_reset_redirect': '/accounts/password/reset/done/',
     'html_email_template_name': 'registration/password_reset_email.html',
     'password_reset_form': EmailValidationOnForgotPassword},
    name="password_reset"),
    #route other accounts URLs to defaults
    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^admin/', admin_site.urls),
    url(r'^stock/$', core_views.reporting.stock_landing_page, name='stock_report'),
    url(r'^shelve/$', core_views.reporting.stock_shelve, name='stock_shelve'),
    url(r'^addboxes/$', core_views.reporting.stock_add_to_shelf, name='stock_add_to_shelf'),
    url(r'^(?P<stock_action>restock)/$', core_views.reporting.stock_report, name='stock_report_restock'),
    url(r'^(?P<stock_action>empty)/$', core_views.reporting.stock_report, name='stock_report_empty'),
    url(r'^api/docs/', include_docs_urls(title='GreenToGo API')),
    url(r'^api/v1/auth/', include('djoser.urls.authtoken')),
    url(r'^api/v1/', include('apiv1.urls')),
    url(r'^$', core_views.index),
    url(r'^accidental_checkout/$', core.views.reporting.accidental_checkout, name='accidental_checkout'),
    url(r'^privacy/$', core.views.registration.privacy, name='privacy')
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
