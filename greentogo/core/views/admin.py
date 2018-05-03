import csv
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.forms import ExportForm

from datetime import date, timedelta, datetime
from postgres_stats import DateTrunc

from core.models import (
    Location, Plan, Restaurant, Subscription, \
    UnclaimedSubscription, User, \
    activity_data, export_chart_data, total_boxes_returned, LocationTag \
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
    checkout_locations = Location.objects.checkout().order_by('name').filter(retired=False)
    checkin_locations = Location.objects.checkin().order_by('name').filter(retired=False)

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


def export_data(request, days=30, *args, **kwargs):
    chartData = False
    if request.method == "POST":
        form = ExportForm(request.POST)
        if form.is_valid():
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')
            chartData = export_chart_data(from_date, to_date)
    else:
        form = ExportForm()
    print(form.is_valid())
    print(form)
    data_json = json.dumps(chartData, cls=DjangoJSONEncoder)
    print(type(data_json))
    view_data = {"data_json": data_json, 'form': form, 'chartData': chartData}
    return render(request, 'admin/export_data.html', view_data)

def export_total_check_out(request, *args, **kwargs):
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    begin_datetime_start_of_day = datetime.combine(datetime.strptime(from_date, '%Y-%m-%d'), datetime.min.time())
    end_datetime_start_of_day = datetime.combine(datetime.strptime(to_date, '%Y-%m-%d'), datetime.min.time())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="check_outs.csv"'

    writer = csv.writer(response)
    tagquery = LocationTag.objects.filter(created_at__gte=begin_datetime_start_of_day, created_at__lte=end_datetime_start_of_day) \
                .annotate(date=DateTrunc('created_at', precision='day'))

    filteredTagQuery = []

    for tags in tagquery:
        if tags.location.service == 'OUT':
            filteredTagQuery.append(tags)

    writer.writerow(['Subscription', 'Username', 'Email', 'Timestamp', 'Location'])
    writer.writerow([len(filteredTagQuery)])    

    for tags in filteredTagQuery:
        writer.writerow([tags.subscription, tags.subscription.user.username, tags.subscription.user.email, tags.created_at, tags.location])
    return response

def export_total_check_in(request, *args, **kwargs):
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    begin_datetime_start_of_day = datetime.combine(datetime.strptime(from_date, '%Y-%m-%d'), datetime.min.time())
    end_datetime_start_of_day = datetime.combine(datetime.strptime(to_date, '%Y-%m-%d'), datetime.min.time())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="check_ins.csv"'

    writer = csv.writer(response)
    tagquery = LocationTag.objects.filter(created_at__gte=begin_datetime_start_of_day, created_at__lte=end_datetime_start_of_day) \
                .annotate(date=DateTrunc('created_at', precision='day'))

    filteredTagQuery = []

    for tags in tagquery:
        if tags.location.service == 'IN':
            filteredTagQuery.append(tags)

    writer.writerow(['Subscription', 'Username', 'Email', 'Timestamp', 'Location'])
    writer.writerow([len(filteredTagQuery)])    

    for tags in filteredTagQuery:
        writer.writerow([tags.subscription, tags.subscription.user.username, tags.subscription.user.email, tags.created_at, tags.location])
    return response

def export_check_out_by_user(request, *args, **kwargs):
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    begin_datetime_start_of_day = datetime.combine(datetime.strptime(from_date, '%Y-%m-%d'), datetime.min.time())
    end_datetime_start_of_day = datetime.combine(datetime.strptime(to_date, '%Y-%m-%d'), datetime.min.time())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="check_outs_by_user.csv"'

    writer = csv.writer(response)
    tagquery = LocationTag.objects.filter(created_at__gte=begin_datetime_start_of_day, created_at__lte=end_datetime_start_of_day) \
                .annotate(date=DateTrunc('created_at', precision='day'))

    filteredTagQuery = []
    for tags in tagquery:
        if tags.location.service == 'OUT':
            filteredTagQuery.append(tags)

    userObjects = []
    for tags in filteredTagQuery:
        newUserObj = User.objects.filter(id=tags.subscription.user_id)
        if not any(elem in userObjects  for elem in newUserObj):
                userObjects.append(newUserObj[0])

    writer.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Total Checked Out'])
    writer.writerow([len(userObjects)])
    
    for users in userObjects:
        total = 0
        for tag in filteredTagQuery:
            if tag.subscription.user.username == users.username:
                total = total + 1
        writer.writerow([users.username, users.email, users.first_name, users.last_name, total])
    return response

def export_check_in_by_user(request, *args, **kwargs):
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    begin_datetime_start_of_day = datetime.combine(datetime.strptime(from_date, '%Y-%m-%d'), datetime.min.time())
    end_datetime_start_of_day = datetime.combine(datetime.strptime(to_date, '%Y-%m-%d'), datetime.min.time())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="check_ins_by_user.csv"'

    writer = csv.writer(response)
    tagquery = LocationTag.objects.filter(created_at__gte=begin_datetime_start_of_day, created_at__lte=end_datetime_start_of_day) \
                .annotate(date=DateTrunc('created_at', precision='day'))

    filteredTagQuery = []
    for tags in tagquery:
        if tags.location.service == 'IN':
            filteredTagQuery.append(tags)

    userObjects = []
    for tags in filteredTagQuery:
        newUserObj = User.objects.filter(id=tags.subscription.user_id)
        if not any(elem in userObjects  for elem in newUserObj):
                userObjects.append(newUserObj[0])

    writer.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Total Checked In'])
    writer.writerow([len(userObjects)])
    
    for users in userObjects:
        total = 0
        for tag in filteredTagQuery:
            if tag.subscription.user.username == users.username:
                total = total + 1
        writer.writerow([users.username, users.email, users.first_name, users.last_name, total])
    return response

def export_check_in_by_location(request, *args, **kwargs):
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    begin_datetime_start_of_day = datetime.combine(datetime.strptime(from_date, '%Y-%m-%d'), datetime.min.time())
    end_datetime_start_of_day = datetime.combine(datetime.strptime(to_date, '%Y-%m-%d'), datetime.min.time())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="check_ins_by_location.csv"'

    writer = csv.writer(response)
    tagquery = LocationTag.objects.filter(created_at__gte=begin_datetime_start_of_day, created_at__lte=end_datetime_start_of_day) \
                .annotate(date=DateTrunc('created_at', precision='day'))

    filteredTagQuery = []
    for tags in tagquery:
        if tags.location.service == 'IN':
            filteredTagQuery.append(tags)

    locationObjects = []
    for tags in filteredTagQuery:
        newLocationObj = Location.objects.filter(id=tags.location.id)
        if not any(elem in locationObjects  for elem in newLocationObj):
            locationObjects.append(newLocationObj[0])

    writer.writerow(['Name', 'Service', 'Total Checked In'])
    writer.writerow([len(locationObjects)])
    
    for location in locationObjects:
        total = 0
        for tag in filteredTagQuery:
            if tag.location.id == location.id:
                total = total + 1
        writer.writerow([location.name, location.service, total])
    return response

def export_check_out_by_location(request, *args, **kwargs):
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    begin_datetime_start_of_day = datetime.combine(datetime.strptime(from_date, '%Y-%m-%d'), datetime.min.time())
    end_datetime_start_of_day = datetime.combine(datetime.strptime(to_date, '%Y-%m-%d'), datetime.min.time())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="check_outs_by_location.csv"'

    writer = csv.writer(response)
    tagquery = LocationTag.objects.filter(created_at__gte=begin_datetime_start_of_day, created_at__lte=end_datetime_start_of_day) \
                .annotate(date=DateTrunc('created_at', precision='day'))

    filteredTagQuery = []
    for tags in tagquery:
        if tags.location.service == 'OUT':
            filteredTagQuery.append(tags)

    locationObjects = []
    for tags in filteredTagQuery:
        newLocationObj = Location.objects.filter(id=tags.location.id)
        if not any(elem in locationObjects  for elem in newLocationObj):
            locationObjects.append(newLocationObj[0])

    writer.writerow(['Name', 'Service', 'Total Checked Out'])
    writer.writerow([len(locationObjects)])
    
    for location in locationObjects:
        total = 0
        for tag in filteredTagQuery:
            if tag.location.id == location.id:
                total = total + 1
        writer.writerow([location.name, location.service, total])
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
