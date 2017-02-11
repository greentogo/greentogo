from django.conf.urls import url
import apiv1.views as views

urlpatterns = [
    url(r'^tag/', views.CheckinCheckoutView.as_view(), name="tag"),
]
