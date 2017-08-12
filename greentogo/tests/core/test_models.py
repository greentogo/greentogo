from datetime import datetime

import pytest

from core.models import Subscription

pytest.mark.usefixtures('betamax_session')


def test_location_has_code(checkin_location):
    assert checkin_location.code is not None


def test_number_of_boxes_for_subscription(subscription2):
    assert subscription2.number_of_boxes == 2


def test_available_boxes_for_subscription(subscription2):
    assert subscription2.available_boxes == 2


def test_available_boxes_after_checkout(subscription2, checkout_location):
    subscription2.tag_location(checkout_location)
    assert subscription2.available_boxes == 1


def test_available_boxes_after_multiple_tags(subscription2, checkin_location, checkout_location):
    subscription2.tag_location(checkout_location)
    subscription2.tag_location(checkout_location)
    subscription2.tag_location(checkin_location)
    subscription2.tag_location(checkout_location)
    subscription2.tag_location(checkin_location)
    subscription2.tag_location(checkin_location)
    subscription2.tag_location(checkout_location)
    assert subscription2.available_boxes == 1


def test_subscription_can_checkout(subscription1, checkout_location):
    assert subscription1.can_checkout()
    subscription1.tag_location(checkout_location)
    assert not subscription1.can_checkout()


def test_checkout_location_keeps_count(subscription2, checkout_location):
    assert checkout_location.get_estimated_stock() == 0

    checkout_location.set_stock(50)
    assert checkout_location.get_estimated_stock() == 50

    subscription2.tag_location(checkout_location)
    assert checkout_location.get_estimated_stock() == 49

    subscription2.tag_location(checkout_location)
    assert checkout_location.get_estimated_stock() == 48

    checkout_location.set_stock(50)
    assert checkout_location.get_estimated_stock() == 50


def test_checkin_location_keeps_count(subscription2, checkout_location, checkin_location):
    assert checkin_location.get_estimated_stock() == 0

    subscription2.tag_location(checkout_location)
    subscription2.tag_location(checkout_location)

    subscription2.tag_location(checkin_location)
    assert checkin_location.get_estimated_stock() == 1

    subscription2.tag_location(checkin_location)
    assert checkin_location.get_estimated_stock() == 2

    checkin_location.set_stock(0)
    assert checkin_location.get_estimated_stock() == 0
