from django.conf.urls import url

import apiv1.views as views

urlpatterns = [
    url(r'^tag/$', views.CheckinCheckoutView.as_view(), name="api_v1_tag"),
    # url(r'^me/$', views.UserView.as_view(), name="api_v1_user"),
    # url(
    #     r'^subscriptions/plans/$',
    #     views.SubscriptionPlansView.as_view(),
    #     name="api_v1_subscription_plans"
    # ),
    # url(
    #     r'^subscriptions/(?P<sub_id>[A-Za-z0-9]+)/$',
    #     views.SubscriptionView.as_view(),
    #     name="api_v1_subscription"
    # ),
    # url(r'^restaurants/', views.RestaurantsView.as_view(), name="api_v1_restaurants"),
]
