from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Location, LocationTag, Plan, Restaurant, Subscription

from .jsend import jsend_error, jsend_fail, jsend_success
from .permissions import HasSubscription
from .serializers import (
    LocationTagSerializer, RestaurantSerializer, SubscriptionSerializer, UserSerializer
)


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


class UserView(APIView):
    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return jsend_success(serializer.data)

# /tag/:number_of_boxes
class CheckinCheckoutView(APIView):
    """Given a location id, create a location tag."""

    permission_classes = (HasSubscription, )

    def post(self, request, number_of_boxes, format=None):
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

        action = request.data["action"]

        if number_of_boxes > plan.number_of_boxes
            return jsend_fail({"action": "too_many_boxes"})

        if action == Location.CHECKIN
            if subscription.boxes_checked_out > number_of_boxes
                return jsend_fail({"action": "cannot_check_in"})

        if action == Location.CHECKOUT
            if subscription.available_boxes < number_of_boxes
                return jsend_fail({"action": "cannot_check_out"})

        if location.service == Location.CHECKIN:
            return self.checkin(subscription, location, number_of_boxes)
        elif location.service == Location.CHECKOUT:
            return self.checkout(subscription, location, number_of_boxes)

    def checkin(self, subscription, location, number_of_boxes):
        tags = []
        for box in range(number_of_boxes):
            tags.append(subscription.tag_location(location))

        if tags.len() > 1
            return jsend_success(LocationTagSerializer(tags, many=True).data)

        return jsend_success(LocationTagSerializer(tags).data)

    def checkout(self, subscription, location, number_of_boxes):
        tags = []
        for box in range(number_of_boxes):
            tags.append(subscription.tag_location(location))

        if tags.len() > 1
            return jsend_success(LocationTagSerializer(tags, many=True).data)

        return jsend_success(LocationTagSerializer(tags).data)


class RestaurantsView(APIView):
    """Returns list of active restaurants"""

    def get(self, request, format=None):
        phases = [1]
        serializer = RestaurantSerializer(Restaurant.objects.filter(phase__in=phases), many=True)
        return jsend_success(serializer.data)
