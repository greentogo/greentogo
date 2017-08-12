import csv

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.models import Location, Plan, Restaurant, Subscription, UnclaimedSubscription, User


def unclaimed_subscription_status_csv(request, *args, **kwargs):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="unclaimed_subscriptions.csv"'

    writer = csv.writer(response)
    writer.writerow(['Email address', 'Subscription plan', 'Claimed'])
    unsubs = UnclaimedSubscription.objects.all()
    for unsub in unsubs:
        writer.writerow([unsub.email, unsub.plan.name, unsub.claimed])
    return response


def restock_locations(request, *args, **kwargs):
    """Present all locations for restock"""
    checkout_locations = Location.objects.checkout().order_by('name')
    return render(request, "admin/restock_locations.html", {'locations': checkout_locations})


@require_POST
def restock_location(request, location_id, *args, **kwargs):
    """Restock a specific location"""
    return _set_stock_count(request, location_id, "admin:restock_locations")


def empty_locations(request, *args, **kwargs):
    """Present all checkin locations for emptying"""
    checkin_locations = Location.objects.checkin().order_by('name')
    return render(request, "admin/empty_locations.html", {'locations': checkin_locations})


@require_POST
def empty_location(request, location_id, *args, **kwargs):
    """Empty a specific location"""
    return _set_stock_count(request, location_id, "admin:empty_locations")


def _set_stock_count(request, location_id, redirect_to):
    location = get_object_or_404(Location, pk=location_id)
    stock_count_str = request.POST['stock_count']
    try:
        stock_count = int(stock_count_str, base=10)
    except ValueError:
        return redirect(reverse(redirect_to))

    if stock_count >= 0:
        location.stock_counts.create(count=stock_count)

    return redirect(reverse(redirect_to))
