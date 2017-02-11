from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import HasSubscription
from .serializers import LocationTagSerializer
from core.models import Location, LocationTag


class CheckinCheckoutView(APIView):
    """Given a location UUID, create a location tag."""

    permission_classes = (HasSubscription, )

    def post(self, request, format=None):
        if not request.data['location']:
            return Response(
                {
                    "detail": "Location must be specified."
                }, status=400)

        subscription = request.subscription

        try:
            location = Location.objects.get(uuid=request.data['location'])
        except Location.DoesNotExist:
            return Response({"detail": "Not a valid location."}, status=400)

        if location.service == Location.CHECKIN:
            return self.checkin(subscription, location)
        elif location.service == Location.CHECKOUT:
            return self.checkout(subscription, location)

    def checkin(self, subscription, location):
        if subscription.can_checkin():
            tag = subscription.tag_location(location)
            return Response(LocationTagSerializer(tag).data)
        else:
            return Response({"detail": "Subscription has no boxes out."})

    def checkout(self, subscription, location):
        if subscription.can_checkout():
            tag = subscription.tag_location(location)
            return Response(LocationTagSerializer(tag).data)
        else:
            return Response({"detail": "Subscription has no available boxes."})
