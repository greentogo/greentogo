from django.conf import settings
from django.http import HttpRequest
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model, authenticate, login
from django.core.mail import send_mail, EmailMultiAlternatives
import json, re, rollbar, urllib.parse, sys

from registration.models import RegistrationProfile
from registration.signals import user_registered
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import User, Location, LocationTag, Plan, Restaurant, Subscription, MobileAppRatings, GroupOrder
from core.forms import UserSignupForm, UserForm

from .jsend import jsend_error, jsend_fail, jsend_success
from .permissions import HasSubscription
from .serializers import CheckinCheckoutSerializer, LocationTagSerializer, UserSerializer, LocationSerializer, RestaurantSerializer, UserRegistrationSerializer, RatingSerializer, CreateGroupOrderSerializer


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
            return self.checkin(subscription, location, serializer.data['number_of_boxes'], request.user)
        elif location.service == Location.CHECKOUT:
            return self.checkout(subscription, location, serializer.data['number_of_boxes'], request.user)

    def checkin(self, subscription, location, number_of_boxes, user):
        if subscription.can_checkin(number_of_boxes):
            tag = subscription.tag_location(location, number_of_boxes, user)
            return jsend_success(LocationTagSerializer(tag, many=True).data)
        else:
            return jsend_fail({"subscription": "Not enough boxes checked out."})

    def checkout(self, subscription, location, number_of_boxes, user):
        if subscription.can_checkout(number_of_boxes):
            tag = subscription.tag_location(location, number_of_boxes, user)
            return jsend_success(LocationTagSerializer(tag, many=True).data)
        else:
            return jsend_fail({"subscription": "Not enough boxes available for checkout."})

# /me/
class UserView(GenericAPIView):
    """
    Get information about the current user, including subscriptions.
    """

    permission_classes = (IsAuthenticated, )
    serializer_class = UserSerializer

    def get(self, request):
        serializer = self.get_serializer(request.user)
        return jsend_success(serializer.data)

    def patch(self, request, format=None):
        serializer = self.get_serializer(request.user)
        saved = 'NO DATA MATCH'
        if 'name' in request.data and 'email' in request.data:
            saved = serializer.updateNameAndEmail(request.user, request.data)
        elif 'expoPushToken' in request.data:
            saved = serializer.updateExpoPushToken(request.user, request.data)

        if saved == 'saved':
            newUser = self.get_serializer(request.user)
            return jsend_success(newUser.data)
        else:
            return jsend_fail({"error": saved}, status=500)


class RateView(GenericAPIView):
    """
    Let user rate mobile app
    """

    permission_classes = (IsAuthenticated, )
    serializer_class = RatingSerializer

    def post(self, request, format=None):
        try:
            MobileAppRatings.objects.create(user=request.user, rating=request.data['rating'], version=request.data['version'])
            return jsend_success(None)
        except Exception as ex:
            rollbar.report_exc_info(sys.exc_info(), request)
            return jsend_fail(None, status=500)


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

        if plandict['boxes'] < subscription.boxes_currently_out():
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
        # serializer = RestaurantSerializer(Restaurant.objects.filter(active=True), many=True)
        serializer = RestaurantSerializer(Location.objects.notRetiredOrAdmin(), many=True)
        for location in serializer.data:
            filtered = re.sub('(- )?(check)?(-)?(in|out)(?:\s|$)', '', location['name'], flags=re.IGNORECASE)
            location['name'] = filtered
        return jsend_success(serializer.data)

class Log(APIView):
    """Logs Errors"""

    def post(self, request, format=None):
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
        try:
            user = User.objects.get(username=username)
        except:
            try:
                user = User.objects.get(email=urllib.parse.unquote(username))
            except:
                return jsend_fail({"error:": "User does not exist"}, status=404)

        data = {
            "total_boxes_returned": LocationTag.objects.checkin().count(),
            "total_user_boxes_returned": user.total_boxes_checkedin(),
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
            rollbar.report_exc_info(sys.exc_info(), request)
            return jsend_fail({"error": "Unable to reset password"}, status=500)

class Register(GenericAPIView):
    """
    User Registration
    """

    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        signupData = {
            'username':request.data.get('username'),
            'email':request.data['email'],
            'email2':request.data['email2'],
            'password1':request.data['password1'],
            'password2':request.data['password2'],
            'tos': ['on']
        }
        try:
            form = UserSignupForm(signupData)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = True
                user.create_stripe_customer()
                user.email = form.cleaned_data.get('email')
                user.save()
                to_email = form.cleaned_data.get('email')
                restaurants = Location.objects.checkout().notRetiredOrAdmin()
                message_data = {
                    'user': user,
                    'restaurants': restaurants,
                    'communityBoxesCheckedIn': int((LocationTag.objects.all()).count()/2) + 100,
                }
                welcome_message_txt = render_to_string('registration/welcome_message.txt', message_data)
                welcome_message_html = render_to_string('registration/welcome_message.html', message_data)
                email = EmailMultiAlternatives(
                    subject='Welcome to GreenToGo!',
                    body=welcome_message_txt,
                    from_email='greentogo@app.durhamgreentogo.com',
                    to=[to_email],
                    reply_to=["amy@durhamgreentogo.com"]
                )
                email.attach_alternative(welcome_message_html, "text/html")
                email.send()
                return jsend_success("Sign Up successful! Now, sign in at our secure web portal and purchase a subscription so that you can use the GreenToGo service!")
            else:
                return jsend_fail(form.errors, status=401)

        except Exception as ex:
            rollbar.report_exc_info(sys.exc_info(), request)
            return jsend_fail({"error": "ERROR"}, status=500)

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
            # print(subscription)
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
            # print(subscription.available_boxes)
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

class GroupOrders(GenericAPIView):
    """Retrives group orders"""

    permission_classes = (IsAuthenticated, )
    serializer_class = CreateGroupOrderSerializer

    def post(self, request):
        try:
            location = Location.objects.filter(code=request.data['location_code']).first()
            if location.service == 'IN':
                return jsend_fail({"error": "Recieved request to create group order at return bin, please check location code"}, status=400)
            sub = Subscription.objects.filter(id=request.data['subscription_id']).first()
            new_group_order = GroupOrder.objects.create(
                subscription=sub,
                corporate_code=sub.corporate_code,
                location=location,
                expected_checkout=request.data['expected_checkout'],
                count=request.data['count'],
            )
            return jsend_success({"data": "received"})
        except Exception as ex:
            rollbar.report_exc_info(sys.exc_info(), request)
            return jsend_fail({"error": "Unable to process request, please try again later"}, status=500)

class GroupOrderCheckout(APIView):
    """Checks out group order"""
    permission_classes = (IsAuthenticated, )
    def post(self, request, group_order_id):
        try:
            GroupOrder.objects.get(id=group_order_id).check_out()
            return jsend_success({"data": "received"})
        except Exception as ex:
            rollbar.report_exc_info(sys.exc_info(), request)
            return jsend_fail({"error": "Unable to process request, please try again later"}, status=500)

class GroupOrderCheckin(APIView):
    """Checks in group order"""
    permission_classes = (IsAuthenticated, )
    def post(self, request, group_order_id):
        try:
            GroupOrder.objects.get(id=group_order_id).check_in()
            return jsend_success({"data": "received"})
        except Exception as ex:
            rollbar.report_exc_info(sys.exc_info(), request)
            return jsend_fail({"error": "Unable to process request, please try again later"}, status=500)
