from datetime import datetime

import pinax.stripe.models as pinax_models
import pytest

from core.models import Subscription

pytest.mark.usefixtures('betamax_session')


def test_location_has_code(checkin_location):
    assert checkin_location.code is not None


def test_number_of_boxes_for_subscription(subscription2):
    assert subscription2.number_of_boxes == 2


def test_available_boxes_for_subscription(subscription2):
    assert subscription2.available_boxes() == 2


def test_available_boxes_after_checkout(subscription2, checkout_location):
    subscription2.tag_location(checkout_location)
    assert subscription2.available_boxes() == 1


def test_available_boxes_after_multiple_tags(subscription2, checkin_location, checkout_location):
    subscription2.tag_location(checkout_location)
    subscription2.tag_location(checkout_location)
    subscription2.tag_location(checkin_location)
    subscription2.tag_location(checkout_location)
    subscription2.tag_location(checkin_location)
    subscription2.tag_location(checkin_location)
    subscription2.tag_location(checkout_location)
    assert subscription2.available_boxes() == 1


def test_subscription_can_checkout(subscription1, checkout_location):
    assert subscription1.can_checkout()
    subscription1.tag_location(checkout_location)
    assert not subscription1.can_checkout()


def test_pinax_subscription_creates_g2g_subscription(user, plan1):
    pinax_sub = pinax_models.Subscription(
        plan=plan1,
        customer=user.customer,
        quantity=1,
        start=datetime.now(),
        status='active',
    )
    pinax_sub.save()

    assert type(pinax_sub.user_subscriptions.get(user=user)) is Subscription


def test_subscription_customer_is_also_subscriber(subscription1):
    assert subscription1.customer.user == subscription1.user
