from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Location, LocationTag, get_plans

from .jsend import jsend_error, jsend_fail, jsend_success
from .permissions import HasSubscription
from .serializers import LocationTagSerializer, SubscriptionSerializer, UserSerializer


# /subscriptions/plans/
# /subscriptions/:id


class SubscriptionPlansView(APIView):
    def get(self, request, format=None):
        plans = get_plans()
        return jsend_success(plans)


class UserView(APIView):
    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return jsend_success(serializer.data)


class CheckinCheckoutView(APIView):
    """Given a location id, create a location tag."""

    permission_classes = (HasSubscription, )

    def post(self, request, format=None):
        if not request.data.get('action'):
            return jsend_fail({"action": "no_action"})

        if request.data['action'] not in [Location.CHECKIN, Location.CHECKOUT]:
            return jsend_fail({"action": "invalid_action"})

        if not request.data.get('location'):
            return jsend_fail({"location": "no_location"})

        subscription = request.subscription

        try:
            location = Location.objects.get(code=request.data['location'])
        except Location.DoesNotExist:
            return jsend_fail({"action": "invalid_location"})

        if location.service != request.data['action']:
            return jsend_fail({"action": "action_and_location_no_match"})

        if location.service == Location.CHECKIN:
            return self.checkin(subscription, location)
        elif location.service == Location.CHECKOUT:
            return self.checkout(subscription, location)

    def checkin(self, subscription, location):
        if subscription.can_checkin():
            tag = subscription.tag_location(location)
            return jsend_success(LocationTagSerializer(tag).data)
        else:
            return jsend_fail({"subscription": "no_boxes_out"})

    def checkout(self, subscription, location):
        if subscription.can_checkout():
            tag = subscription.tag_location(location)
            return jsend_success(LocationTagSerializer(tag).data)
        else:
            return jsend_fail({"subscription": "no_boxes_available"})
