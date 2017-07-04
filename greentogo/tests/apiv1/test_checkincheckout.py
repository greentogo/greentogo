from rest_framework.test import force_authenticate

from apiv1.views import CheckinCheckoutView
from core.models import Location


def test_no_action(apirf, subscription1, checkin_location):
    user = subscription1.customer.user

    request = apirf.post(
        '/api/v1/tag', {"subscription": subscription1.pk,
                        "location": checkin_location.code},
        format="json"
    )

    force_authenticate(request, user=user)
    response = CheckinCheckoutView.as_view()(request)

    assert response.status_code == 400
    assert response.data['data']['action'] == "no_action"


def test_no_location(apirf, subscription1, checkin_location):
    user = subscription1.customer.user

    request = apirf.post(
        '/api/v1/tag', {"action": Location.CHECKIN,
                        "subscription": subscription1.pk},
        format="json"
    )

    force_authenticate(request, user=user)
    response = CheckinCheckoutView.as_view()(request)

    assert response.status_code == 400
    assert response.data['data']['location'] == "no_location"


def test_action_location_no_match(apirf, subscription1, checkin_location):
    user = subscription1.customer.user

    request = apirf.post(
        '/api/v1/tag', {
            "action": Location.CHECKOUT,
            "subscription": subscription1.pk,
            "location": checkin_location.code
        },
        format="json"
    )

    force_authenticate(request, user=user)
    response = CheckinCheckoutView.as_view()(request)

    assert response.status_code == 400
    assert response.data['data']['action'] == "action_and_location_no_match"


def test_valid_checkin(apirf, subscription1, checkin_location, checkout_location):
    user = subscription1.customer.user

    # We have to have a box checked out to check one in.
    subscription1.tag_location(checkout_location)

    request = apirf.post(
        '/api/v1/tag/', {
            "action": Location.CHECKIN,
            "subscription": subscription1.pk,
            "location": checkin_location.code
        },
        format="json"
    )
    force_authenticate(request, user=user)
    response = CheckinCheckoutView.as_view()(request)

    assert response.status_code == 200
    assert response.data['data']['service'] == checkin_location.service
    assert response.data['data']['available_boxes'] == 1


def test_invalid_checkin(apirf, subscription1, checkin_location):
    user = subscription1.customer.user

    request = apirf.post(
        '/api/v1/tag/', {
            "action": Location.CHECKIN,
            "subscription": subscription1.pk,
            "location": checkin_location.code
        },
        format="json"
    )
    force_authenticate(request, user=user)
    response = CheckinCheckoutView.as_view()(request)

    assert response.status_code == 400
    assert response.data['data']['subscription'] == 'no_boxes_out'


def test_valid_checkout(apirf, subscription1, checkout_location):
    user = subscription1.customer.user

    request = apirf.post(
        '/api/v1/tag/', {
            "action": Location.CHECKOUT,
            "subscription": subscription1.pk,
            "location": checkout_location.code
        },
        format="json"
    )
    force_authenticate(request, user=user)
    response = CheckinCheckoutView.as_view()(request)

    assert response.status_code == 200
    assert response.data['data']['service'] == checkout_location.service
    assert response.data['data']['available_boxes'] == 0


def test_invalid_checkout(apirf, subscription1, checkout_location):
    user = subscription1.customer.user

    # We have to have a box checked out to cause an error.
    subscription1.tag_location(checkout_location)

    request = apirf.post(
        '/api/v1/tag/', {
            "action": Location.CHECKOUT,
            "subscription": subscription1.pk,
            "location": checkout_location.code
        },
        format="json"
    )
    force_authenticate(request, user=user)
    response = CheckinCheckoutView.as_view()(request)

    assert response.status_code == 400
    assert response.data['data']['subscription'] == 'no_boxes_available'
