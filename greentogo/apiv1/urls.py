from django.conf.urls import url

import apiv1.views as views

urlpatterns = [
    url(r'^tag/$', views.CheckinCheckoutView.as_view(), name="tag"),
    url(r'^me/$', views.UserView.as_view(), name="user"),
    url(r'^subscriptions/', views.SubscriptionsView.as_view(), name="subscriptions")
]
