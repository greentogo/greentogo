from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import pluralize
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.urls import reverse
from django.utils.safestring import mark_safe

from core.models import Location, Subscription, LocationTag, User

@login_required
def dashboard_home(request):
    if request.user.restaurant_manager.first() is None:
      return HttpResponse("Access Denied")
    return redirect('dashboard', request.user.restaurant_manager.first().code)

@login_required
def dashboard(request, location_code):
    restaurant = get_object_or_404(Location, code=location_code)
    try:
        request.user.restaurant_manager.get(code=location_code)
    except Location.DoesNotExist:
        return HttpResponse("Access Denied")
    return render(request, "dashboard/dashboard.html", {
      "restaurant":restaurant
      })

