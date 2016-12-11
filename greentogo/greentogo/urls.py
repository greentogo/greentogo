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
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView

from beta_signup import views

urlpatterns = [
    url(r'^$', views.SubscriptionView.as_view(), name='payment'),
    url(r'^beta-subscribe/$', views.SubscriptionView.as_view(),
        name="beta-subscribe"),
    url(r'^thanks/', TemplateView.as_view(template_name="thanks.html"),
        name="beta-thanks"),
    url(r'^error/', TemplateView.as_view(template_name="error.html"),
        name="beta-error"),
    url(r'^admin/', admin.site.urls),
]
