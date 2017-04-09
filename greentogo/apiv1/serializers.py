from rest_framework import serializers

from core.models import LocationTag, available_boxes_for_subscription


class LocationTagSerializer(serializers.Serializer):
    subscription = serializers.CharField(source="subscription.stripe_id")
    location = serializers.CharField(source="location.code")
    service = serializers.CharField(source="location.service")
    available_boxes = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()

    def get_available_boxes(self, obj):
        return available_boxes_for_subscription(obj.subscription)
