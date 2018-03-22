import csv
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.models import (
    Location, Plan, Restaurant, Subscription, \
    UnclaimedSubscription, User, \
    activity_data, total_boxes_returned, \
)


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


def stock_report(request, *args, **kwargs):
    """Show a report of current stock at each location."""
    checkout_locations = Location.objects.checkout().order_by('name')
    checkin_locations = Location.objects.checkin().order_by('name')

    checkout_data = {
        "names": [],
        "count": [],
    }

    for loc in checkout_locations:
        checkout_data["names"].append(loc.name)
        checkout_data["count"].append(loc.get_estimated_stock())

    checkin_data = {
        "names": [],
        "count": [],
    }

    for loc in checkin_locations:
        checkin_data["names"].append(loc.name)
        checkin_data["count"].append(loc.get_estimated_stock())

    def get_estimated_at_checkout():
        count = sum([l.get_estimated_stock() for l in
            Location.objects.checkout()])
        return count

    def get_estimated_at_checkin():
        count = sum([l.get_estimated_stock() for l in
            Location.objects.checkin()])
        return count

    def get_estimated_checkedout():
        count = sum([s.boxes_checked_out for s in
            Subscription.objects.active()])
        return count

    cycle_data = {
        "labels": [
            "Clean at restaurants",
            "Checked out",
            "Dirty", #this should expand to 3 categories
        ],
        "count": [
            get_estimated_at_checkout(),
            get_estimated_checkedout(),
            get_estimated_at_checkin(),
        ],
    }

    return render(
        request, "admin/stock_report.html",
        {
            "data_json":json.dumps(dict(
                checkin=checkin_data, 
                checkout=checkout_data,
                cycle=cycle_data,
        ))}
    )


def activity_report(request, days=30, *args, **kwargs):
    data = activity_data(days)
    data_json = json.dumps(data, cls=DjangoJSONEncoder)
    view_data = {"data_json": data_json, "total_boxes_returned": total_boxes_returned()}
    return render(request, 'admin/activity_report.html', view_data)


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
