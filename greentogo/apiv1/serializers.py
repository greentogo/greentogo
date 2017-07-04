from django.contrib.auth import get_user_model

from rest_framework import serializers

from core.models import (
    LocationTag, Subscription, available_boxes_for_subscription, max_boxes_for_subscription
)


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('name', 'available_boxes', 'max_boxes', )

    name = serializers.CharField(source="display_name")

    available_boxes = serializers.SerializerMethodField()
    max_boxes = serializers.SerializerMethodField()

    def get_max_boxes(self, obj):
        return max_boxes_for_subscription(obj.pinax_subscription)

    def get_available_boxes(self, obj):
        return available_boxes_for_subscription(obj.pinax_subscription)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('name', 'email', 'subscriptions', )

    subscriptions = SubscriptionSerializer(many=True)


class LocationTagSerializer(serializers.Serializer):
    subscription = serializers.CharField(source="subscription.stripe_id")
    location = serializers.CharField(source="location.code")
    service = serializers.CharField(source="location.service")
    available_boxes = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()

    def get_available_boxes(self, obj):
        return available_boxes_for_subscription(obj.subscription)
