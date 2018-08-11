from django.conf import settings
from django.http import HttpRequest
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
import json

from registration.models import RegistrationProfile
from registration.signals import user_registered
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import User, Location, LocationTag, Plan, Restaurant, Subscription
from core.forms import UserSignupForm
import rollbar

from .jsend import jsend_error, jsend_fail, jsend_success
from .permissions import HasSubscription
from .serializers import CheckinCheckoutSerializer, LocationTagSerializer, UserSerializer, LocationSerializer, RestaurantSerializer


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
        serializer = RestaurantSerializer(Restaurant.objects.filter(active=True), many=True)
        return jsend_success(serializer.data)

class Log(APIView):
    """Logs Errors"""

    def post(self, request, format=None):
        request.body = {
            "AHHH":"OH NO"
        }
        # body_unicode = request.body.decode('utf-8')
        # body = json.loads(body_unicode)
        # print(body)
        rollbar.report_message(request.body, "error")
        return jsend_success({"data": "received"})


class Statistics(GenericAPIView):
    """
    Get stats for box returns, users and subscriptions
    """

    permission_classes = (IsAuthenticated, )
    # Tell DRF documentation you are not a list view.
    action = 'retrieve'

    def get(self, request, username):
        boxesCheckedIn = 0
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return jsend_fail({"error:": "User does not exist"}, status=404)
        for sub in user.get_subscriptions():
            boxesCheckedIn = boxesCheckedIn + int((LocationTag.objects.filter(subscription_id=sub.id)).count()/2)
        data = {
            "total_boxes_returned": LocationTag.objects.checkin().count(),
            "total_user_boxes_returned": boxesCheckedIn,
            "total_active_subscriptions": Subscription.objects.active().count(),
            }
        return jsend_success(data)

class PasswordReset(APIView):
    """
    Password Reset
    """

    def post(self, request):
        try:
            user = None
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            userString = body['userString']

            user = User.objects.filter(email=userString).first() or User.objects.filter(username=userString).first()

            if user is not None:

                form = PasswordResetForm({'email': user.email})
                if form.is_valid():
                    request = HttpRequest()
                    request.META['SERVER_NAME'] = 'app.durhamgreentogo.com'
                    request.META['SERVER_PORT'] = '443'
                    form.save(
                        request= request,
                        use_https=True,
                        from_email="purchases@durhamgreentogo.com", 
                        email_template_name='registration/password_reset_email.html')
                return jsend_success("Success! Please check your email for password reset instructions.")

            else:
                return jsend_fail({"error": "User does not exist"}, status=404)

        except Exception as ex:
            return jsend_fail({"error": "Unable to reset password"}, status=500)
            rollbar.report_exc_info(sys.exc_info(), request)

class RfidView(APIView):
    """
    Get and Put for rfid chips to checkout or checkin a box 
    """


    def get(self, request, location_code, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return jsend_fail({"error:": "User does not exist"}, status=404)

        try:
            location = Location.objects.get(code=location_code)
        except Location.DoesNotExist:
            return jsend_fail({"error:": "Location does not exist"}, status=404)

        if user.has_active_subscription():
            for sub in user.get_subscriptions():
                if sub.available_boxes > 1:
                    subscription = sub
                    break
            print(subscription)
            # serializer = SubscriptionSerializer(subscription)
            data = {
                "Boxes Avail": subscription.available_boxes,
                "Boxes Max": subscription.max_boxes,
                "User Email": user.email,
                "location": location.name
                }
            return jsend_success(data)
        else:
            return jsend_fail({"error:": "User exists but has no active subscriptions"}, status=401)

    def put(self, request, location_code, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return jsend_fail({"error:": "User does not exist"}, status=404)

        try:
            location = Location.objects.get(code=location_code)
        except Location.DoesNotExist:
            return jsend_fail({"error:": "Location does not exist"}, status=404)

        if user.has_active_subscription():
            for sub in user.get_subscriptions():
                if sub.available_boxes > 1:
                    subscription = sub
                    break
            print(subscription.available_boxes)
            if subscription:
                subscription.tag_location(location, 1)
                data = {
                    "msg": "1 box checked {}! {} out of {} now avaiable".format(location.service, subscription.available_boxes, subscription.max_boxes)
                    }
                return jsend_success(data)
            else: 
                return jsend_fail({"error:": "User has no boxes left in subscription"}, status=403)
        else:
            return jsend_fail({"error:": "User exists but has no active subscriptions"}, status=403)