from rest_framework.permissions import IsAuthenticated

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
