"""
Views for reporting stock counts/actuals and resetting
"""

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils.safestring import mark_safe
from collections import OrderedDict
from itertools import groupby

from django.http import HttpResponse

from core.models import LocationStockCount, LocationStockReport, Location, Restaurant
from core.forms import AccidentalCheckoutForm

@staff_member_required()
def stock_landing_page(request):
    """
    This view is for figuring out which view you should use!
    """
    return render(request,'reporting/stock_landing_page.html')

@staff_member_required()
def stock_shelve(request):
    """
    This view is for returning clean boxes to g2g headquarters
    """
    if request.method == 'POST':
        try:
            location = Location.objects.checkin().get(admin_location=True)
            stock_count = request.POST.get('stock_count')
            estimated_amount = location.get_estimated_stock()
            new_count = estimated_amount + int(stock_count)
            location.stock_counts.create(count=new_count)
            messages.info(request,"{} clean boxes successfully shelved at GreenToGo HQ!".format(stock_count))
        except:
            messages.error(request,"There are no headquarter locations! Add one by assigning an admin location")

    return render(request,'reporting/shelve.html',{ })


@staff_member_required()
def stock_report(request, stock_action):
    """
    This view is for restocking/emptying locations
    """
    if request.method == 'POST':
        location = Location.objects.get(pk=request.POST.get('location'))
        actual_count = request.POST.get('actual_count')
        stock_count = request.POST.get('stock_count')
        #create a stock report and a stock count for the location
        location.stock_reports.create(actual_amount=actual_count)
        location.stock_counts.create(count=stock_count)
        try:
            if stock_action == 'restock':
                #subtract restocked boxes from the admin total
                admin_location = Location.objects.checkin().get(admin_location=True)
                new_count = admin_location.get_estimated_stock() - int(stock_count)
                admin_location.stock_counts.create(count=new_count)
        except:
            pass
        messages.success(request,"Successfully stocked and submitted a report for {}".format(location))

    if stock_action == 'restock':
        locations = Location.objects.checkout()
        locations = locations.filter(retired=False)
    else:
        locations = Location.objects.checkin()
        locations = locations.filter(retired=False)
    return render(request,'reporting/stock.html',{
        "locations": locations,
        "stock_action": stock_action,
    })


"""
Callback for when a user has accidentally checked out a box.
Should check if the user can check in the amount of boxes that
they are requesting to check in, change the inventory, and then
tell the user how many boxes they have remaining.
"""
@login_required
def accidental_checkout(request):
    if request.method == 'POST':
        form = AccidentalCheckoutForm(request.POST)
        if form.is_valid():
            form_location = form.cleaned_data['location']
            location = get_object_or_404(Location, name=form_location)
            number_of_boxes = form.cleaned_data['num_boxes']
            user = request.user
            available_boxes = 0
            box_plural = lambda n: pluralize(n, "box,boxes")
            for sub in user.subscriptions.active():
                if sub.can_tag_location(location, number_of_boxes):
                    sub.tag_location(location, number_of_boxes)
                    available_boxes = sub.available_boxes
                    msg = "Thank you for returning {} {}!" \
                    "You have {} {} remaining.".format(number_of_boxes, box_plural(number_of_boxes), available_boxes, box_plural(available_boxes))
                    messages.success(request, msg)
                else:
                    msg = "You cannot currently check in {} {}.".format(number_of_boxes, box_plural(number_of_boxes))
                    messages.error(request, msg)
            return render(request, "reporting/thank_you.html", {
                "boxes_available": available_boxes,
            })
    else:
        form = AccidentalCheckoutForm()
        return render(request, "reporting/accidental_checkout.html", {
            "form": form
        })
