from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render

from registration.models import RegistrationProfile
from registration.signals import user_registered
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import User, Location, LocationTag, Plan, Restaurant, Subscription

from .jsend import jsend_error, jsend_fail, jsend_success
from .permissions import HasSubscription
from .serializers import CheckinCheckoutSerializer, LocationTagSerializer, UserSerializer, LocationSerializer


class CheckinCheckoutView(GenericAPIView):
    """
    Check a box in or out.
    """

    permission_classes = (IsAuthenticated, HasSubscription, )
    serializer_class = CheckinCheckoutSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        subscription = request.subscription

        if not serializer.is_valid():
            return jsend_fail(serializer.errors)

        location = Location.objects.get(code=serializer.data['location'])

        if location.service == Location.CHECKIN:
            return self.checkin(subscription, location, serializer.data['number_of_boxes'])
        elif location.service == Location.CHECKOUT:
            return self.checkout(subscription, location, serializer.data['number_of_boxes'])

    def checkin(self, subscription, location, number_of_boxes):
        if subscription.can_checkin(number_of_boxes):
            tag = subscription.tag_location(location, number_of_boxes)
            return jsend_success(LocationTagSerializer(tag, many=True).data)
        else:
            return jsend_fail({"subscription": "Not enough boxes checked out."})

    def checkout(self, subscription, location, number_of_boxes):
        if subscription.can_checkout(number_of_boxes):
            tag = subscription.tag_location(location, number_of_boxes)
            return jsend_success(LocationTagSerializer(tag, many=True).data)
        else:
            return jsend_fail({"subscription": "Not enough boxes available for checkout."})


class UserView(GenericAPIView):
    """
    Get information about the current user, including subscriptions.
    """

    permission_classes = (IsAuthenticated, )
    serializer_class = UserSerializer
    # Tell DRF documentation you are not a list view.
    action = 'retrieve'

    def get(self, request):
        serializer = self.get_serializer(request.user)
        return jsend_success(serializer.data)


class LocationView(GenericAPIView):
    """
    Get information about Locations
    """

    permission_classes = (IsAuthenticated, )
    # serializer_class = LocationSerializer
    # Tell DRF documentation you are not a list view.
    action = 'retrieve'

    def get(self, request, location_code):
        try:
            location = Location.objects.get(code=location_code)
        except Location.DoesNotExist:
            location = None
            return jsend_fail({"error": "Location does not exist"}, status=200)

        serializer = LocationSerializer(location)
        return jsend_success(serializer.data)    


# /subscriptions/:id
class SubscriptionView(APIView):
    def get_object(self, request, subscription_id):
        #return Subscription.lookup_by_customer_and_sub_id(request.user.customer, subscription_id)
        return Subscription.objects.owned_by(request.user).get(pk=subscription_id)

    def get(self, request, sub_id, format=None):
        try:
            subscription = self.get_object(request, sub_id)
        except Subscription.DoesNotExist:
            return jsend_fail({"subscription": "not_subscription_owner"}, status=401)

        serializer = SubscriptionSerializer(subscription)
        return jsend_success(serializer.data)

    def put(self, request, sub_id, format=None):
        try:
            subscription = self.get_object(request, sub_id)
        except Subscription.DoesNotExist:
            return jsend_fail({"subscription": "not_subscription_owner"}, status=401)

        if not request.data.get('plan'):
            return jsend_fail({"plan": "no_plan"})

        plan = pinax_models.Plan.objects.get(stripe_id=request.data.get('plan'))
        plandict = plan.as_dict()

        if plandict['boxes'] < subscription.boxes_checked_out():
            return jsend_fail({"plan": "plan_not_enough_boxes"})

        subscriptions.update(
            subscription=subscription.pinax_subscription,
            plan=plan,
            prorate=True,
            charge_immediately=True
        )
        invoices.create(customer=request.user.customer)

        # Reload subscription
        subscription = self.get_object(request, sub_id)
        serializer = SubscriptionSerializer(subscription)
        return jsend_success(serializer.data)


# /subscriptions/plans/
class SubscriptionPlansView(APIView):
    def get(self, request, format=None):
        plans = Plans.objects.available().as_dicts()
        return jsend_success(plans)


class RestaurantsView(APIView):
    """Returns list of active restaurants"""

    def get(self, request, format=None):
        phases = [1]
        serializer = RestaurantSerializer(Restaurant.objects.filter(phase__in=phases), many=True)
        return jsend_success(serializer.data)

class Statistics(GenericAPIView):
    """
    Get stats for box returns, users and subscriptions
    """

    permission_classes = (IsAuthenticated, )
    # Tell DRF documentation you are not a list view.
    action = 'retrieve'

    def get(self, request):
        data = {
            "total_boxes_returned": LocationTag.objects.checkin().count(),
            "total_users": User.objects.count(),
            "total_subscriptions": Subscription.objects.active().count(),

            }
        return jsend_success(data)
