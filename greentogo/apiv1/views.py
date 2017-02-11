from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import HasSubscription
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
            subscription.tag_location(location)
            return Response({
                "service": location.service,
                "subscription": subscription.pk,
                "location": location.uuid,
                "available_boxes": subscription.available_boxes()
            })
        else:
            return Response({"detail": "Subscription has no boxes out."})

    def checkout(self, subscription, location):
        if subscription.can_checkout():
            subscription.tag_location(location)
            return Response({
                "service": location.service,
                "subscription": subscription.pk,
                "location": location.uuid,
                "available_boxes": subscription.available_boxes()
            })
        else:
            return Response({"detail": "Subscription has no available boxes."})
