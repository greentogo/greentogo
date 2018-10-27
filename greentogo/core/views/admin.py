import csv
import json

from django.contrib import messages
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
    UnclaimedSubscription, User, send_push_message, \
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
    checkout_locations = Location.objects.checkout().order_by('name').filter(retired=False, admin_location=False)
    checkin_locations = Location.objects.checkin().order_by('name').filter(retired=False, admin_location=False)
    admin_locations = Location.objects.checkin().order_by('name').filter(retired=False, admin_location=True)
    washlocation = Location.objects.checkin().get(retired=False, washing_location=True)
    hqLocation = Location.objects.checkin().get(retired=False, headquarters=True)

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

    admin_data = {
        "names": [],
        "count": [],
    }

    for loc in admin_locations:
        admin_data["names"].append(loc.name)
        admin_data["count"].append(loc.get_estimated_stock())

    def get_estimated_at_checkout():
        count = sum([l.get_estimated_stock() for l in
            Location.objects.checkout()])
        return count

    def get_estimated_at_checkin():
        count = sum([l.get_estimated_stock() for l in
            checkin_locations])
        return count

    def get_estimated_checkedout():
        count = sum([s.boxes_currently_out for s in
            Subscription.objects.active()])
        return count

    def get_estimated_at_wash():
        count = washlocation.get_estimated_stock()
        return count

    def get_estimated_at_hq():
        count = hqLocation.get_estimated_stock()
        return count

    cycle_data = {
        "labels": [
            "Clean at restaurants",
            "Checked out",
            "Dirty at return stations", #this should expand to 3 categories, two of them is below
            "Dirty and being washed",
            "Clean at G2G HQ",
        ],
        "count": [
            get_estimated_at_checkout(),
            get_estimated_checkedout(),
            get_estimated_at_checkin(),
            get_estimated_at_wash(),
            get_estimated_at_hq(),
        ],
    }

    return render(
        request, "admin/stock_report.html",
        {
            "data_json":json.dumps(dict(
                checkin=checkin_data, 
                checkout=checkout_data,
                admin=admin_data,
                cycle=cycle_data
        ))}
    )


def user_report(request,*args, **kwargs):
    data = User.objects.all()
    view_data = {"data": data}
    return render(request, 'admin/user_report.html', view_data)


def activity_report(request, days=30, *args, **kwargs):
    data = activity_data(days)
    data_json = json.dumps(data, cls=DjangoJSONEncoder)
    view_data = {"data_json": data_json, "total_boxes_returned": total_boxes_returned()}
    return render(request, 'admin/activity_report.html', view_data)


def restock_locations(request, *args, **kwargs):
    """Present all locations for restock"""
    checkout_locations = Location.objects.checkout().order_by('name')
    return render(request, "admin/restock_locations.html", {'locations': checkout_locations})


def mobile_application(request, *args, **kwargs):
    if request.method == "POST":
        try:
            message = request.POST.get('push-notification-message')
            title = request.POST.get('push-notification-title')
            usersWithPushTokens = User.objects.getPushTokens()
            for user in usersWithPushTokens:
                send_push_message(user.expoPushToken, title, message)
            messages.add_message(request, messages.INFO, 'Messages sent!')
        except:
            messages.add_message(request, messages.ERROR, 'ERROR SENDING MESSAGE, UNABLE TO SEND')
    return render(request, 'admin/mobile_application.html')


@require_POST
def restock_location(request, location_id, *args, **kwargs):
    """Restock a specific location"""
    return _set_stock_count(request, location_id, "admin:restock_locations")


def empty_locations(request, *args, **kwargs):
    """Present all checkin locations for emptying"""
    checkin_locations = Location.objects.checkin().order_by('name').get(admin_location=False)
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
    data_json = json.dumps(chartData, cls=DjangoJSONEncoder)
    view_data = {"data_json": data_json, 'form': form, 'chartData': chartData}
    return render(request, 'admin/export_data.html', view_data)

# TODO All of the exports below are ugly repeat code. Consolidate into one function!
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

def export_subscriptions(request, *args, **kwargs):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_subscriptions.csv"'

    writer = csv.writer(response)
    subs = Subscription.objects.all()

    writer.writerow(['starts at', 'ends at', 'plan', 'user', 'email', 'stripe id', 'stripe status', 'cancelled_by_user',  'corporate_code_id', 'coupon_code_id', 'is_active', 'total_checkouts', ])

    for sub in subs:
        writer.writerow([sub.starts_at, sub.ends_at, sub.plan, sub.user, sub.user.email, sub.stripe_id, sub.stripe_status, sub.cancelled, sub.corporate_code_id, sub.coupon_code_id, sub.is_active, sub.total_checkouts()])
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
# TODO All of the exports above are ugly repeat code. Consolidate into one function!

def export_user_reports(request, *args, **kwargs):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_reports.csv"'

    writer = csv.writer(response)
    userquery = User.objects.all()

    writer.writerow(['Username', 'Name', 'Email', 'Date Joined', 'Last Login', 'Subscription Level', 'Coupon Code', 'Corp Code', 'Stripe'])
    writer.writerow([len(userquery)])
    
    for user in userquery:
        subs = Subscription.objects.filter(user=user).order_by('-ends_at')
        if len(subs) > 0:
            writer.writerow([user.username, user.name, user.email, user.date_joined, user.last_login, subs[0].plan, subs[0].coupon_code_id, subs[0].corporate_code_id, subs[0].stripe_id])
        else:
            writer.writerow([user.username, user.name, user.email, user.date_joined, user.last_login, '', '', '', ''])
    return response
