from rest_framework import serializers
from core.models import LocationTag


class LocationTagSerializer(serializers.Serializer):
    subscription = serializers.IntegerField(source="subscription.pk")
    location = serializers.CharField(source="location.uuid")
    service = serializers.CharField(source="location.service")
    available_boxes = serializers.IntegerField(
        source="subscription.available_boxes")
    created_at = serializers.DateTimeField()
