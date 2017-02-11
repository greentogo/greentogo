from rest_framework.permissions import IsAuthenticated
from core.models import Subscription


class IsSubscriber(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request,
                                      view) and request.user.subscriber


class HasSubscription(IsSubscriber):
    def has_permission(self, request, view):
        is_subscriber = super().has_permission(request, view)
        if not is_subscriber:
            return False

        subscriber = request.user.subscriber
        try:
            subscription = subscriber.subscriptions.get(
                pk=request.data['subscription'])
            request.subscription = subscription
            return True
        except KeyError:
            return False
        except Subscription.DoesNotExist:
            return False
