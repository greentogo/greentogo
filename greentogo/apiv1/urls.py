from django.conf.urls import include, url
# from django.contrib.auth import views as auth_views
# from core.forms import EmailValidationOnForgotPassword
import apiv1.views as views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^tag/$', views.CheckinCheckoutView.as_view(), name="api_v1_tag"),
    url(r'^me/$', views.UserView.as_view(), name="api_v1_user"),
    url(r'^rate/$', views.RateView.as_view(), name="api_v1_rate"),
    url(r'^stats/(?P<username>.*)/$', views.Statistics.as_view(), name="api_v1_stats"),
    url(r'^locations/(?P<location_code>[A-Za-z0-9]+)/$', views.LocationView.as_view(), name="api_v1_location"),
    url(
        r'^subscriptions/plans/$',
        views.SubscriptionPlansView.as_view(),
        name="api_v1_subscription_plans"
    ),
    url(
        r'^subscriptions/(?P<sub_id>[A-Za-z0-9]+)/$',
        views.SubscriptionView.as_view(),
        name="api_v1_subscription"
    ),
    url(r'^restaurants/', views.RestaurantsView.as_view(), name="api_v1_restaurants"),
    url(
        r'^rfid/locationcode/(?P<location_code>\w+)/username/(?P<username>\w+)$',
        views.RfidView.as_view(),
        name="RfidView"
    ),
    url(r'^password/reset/$',  views.PasswordReset.as_view(), name="PasswordReset"),
    url(r'^register/', views.Register.as_view(), name="Register"),
    url(r'^log/$',  views.Log.as_view(), name="Log"),
    url(r'^group/$',  views.GroupOrders.as_view(), name="Group Orders"),
    url(r'^group/out/(?P<group_order_id>[A-Za-z0-9]+)/$',  views.GroupOrderCheckout.as_view(), name="Group Orders"),
    url(r'^group/in/(?P<group_order_id>[A-Za-z0-9]+)/$',  views.GroupOrderCheckin.as_view(), name="Group Orders"),
]
