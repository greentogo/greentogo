from rest_framework.permissions import BasePermission, IsAuthenticated

from core.models import Subscription


class HasSubscription(IsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        if not is_authenticated:
            return False
        user = request.user
        try:
            subscription = user.subscriptions.get(pk=request.data['subscription'])
            request.subscription = subscription
            return True
        except KeyError:
            return False
        except Subscription.DoesNotExist:
            return False


class IsSubscriptionOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
