from django.contrib.auth import get_user_model

from rest_framework import serializers

from core.models import LocationTag, Restaurant, Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', 'name', 'available_boxes', 'max_boxes', )

    name = serializers.CharField(source="display_name")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('name', 'email', 'subscriptions', )

    subscriptions = SubscriptionSerializer(many=True)


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
        model = Restaurant
        fields = ('name', 'address', 'latitude', 'longitude', 'phase')

    name = serializers.CharField()
    address = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    phase = serializers.IntegerField()
