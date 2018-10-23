from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.validators import UniqueValidator
from core.forms import UserSignupForm
from django.db.utils import IntegrityError

from core.models import Location, LocationTag, Restaurant, Subscription, User, MobileAppRatings


class CheckinCheckoutSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=[Location.CHECKIN, Location.CHECKOUT])
    location = serializers.CharField(max_length=6)
    subscription = serializers.IntegerField()
    number_of_boxes = serializers.IntegerField(min_value=1, default=1)

    def validate_location(self, value):
        try:
            location = Location.objects.get(code=value)
        except Location.DoesNotExist:
            raise ValidationError("Location does not exist.")
        return value

    def validate(self, data):
        location = Location.objects.get(code=data['location'])
        if location.service != data['action']:
            raise ValidationError("Invalid action for this location.")
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', 'name', 'available_boxes', 'max_boxes', )

    name = serializers.CharField(source="display_name")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('name', 'email', 'username', 'subscriptions', 'expoPushToken', )

    subscriptions = SubscriptionSerializer(many=True)
    def updateNameAndEmail(self, instance, data):
        try:
            instance.name = data['name']
            instance.email = data['email']
            instance.save()
            return 'saved'
        except IntegrityError:
            return 'User with this Email address already exists.'
        except: 
            return 'Error, please try again later.'

    def updateExpoPushToken(self, instance, data):
        try:
            instance.expoPushToken = data['expoPushToken']
            instance.save()
            return 'saved'
        except: 
            return 'Error, please try again later.'

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileAppRatings
        fields = ('rating', 'version')


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('service', 'address', 'code', 'name')

    service = serializers.CharField()
    address = serializers.CharField()
    code = serializers.CharField()
    name = serializers.CharField()


class LocationTagSerializer(serializers.Serializer):
    subscription = serializers.IntegerField(source="subscription.id")
    location = serializers.CharField(source="location.code")
    service = serializers.CharField(source="location.service")
    available_boxes = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()

    def get_available_boxes(self, obj):
        return obj.subscription.available_boxes


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('name', 'address', 'latitude', 'longitude', 'service')

    name = serializers.CharField()
    address = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    service = serializers.CharField()

class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    email = serializers.CharField(max_length=255)
    email2 = serializers.CharField(max_length=255)
    password1 = serializers.CharField(max_length=255)
    password2 = serializers.CharField(max_length=255)