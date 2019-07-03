from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

from core.models import Location, User

@login_required
def dashboard_home(request):
    if request.user.restaurant_manager.first() is None:
      return HttpResponse("Access Denied")
    return redirect('dashboard', request.user.restaurant_manager.first().code)

@login_required
def dashboard(request, location_code):
    restaurant = get_object_or_404(Location, code=location_code)
    if not request.user.is_superuser:
      try:
          request.user.restaurant_manager.get(code=location_code)
      except Location.DoesNotExist:
          return HttpResponse("Access Denied")
    return render(request, "dashboard/dashboard.html", {
      "restaurant":restaurant,
      "num_users": User.objects.all().count()
    })

