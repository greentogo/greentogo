def test_location_has_uuid(checkin_location):
    assert checkin_location.uuid is not None


def test_subscription_has_admin(subscription1):
    assert subscription1.admin is not None


def test_available_boxes_for_subscription(subscription2):
    assert subscription2.available_boxes() == 2


def test_available_boxes_after_checkout(subscription2, checkout_location):
    subscription2.tag_location(checkout_location)
    assert subscription2.available_boxes() == 1
