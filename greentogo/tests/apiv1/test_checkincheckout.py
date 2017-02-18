from rest_framework.test import force_authenticate
from apiv1.views import CheckinCheckoutView


def test_valid_checkin(apirf, subscription1, checkin_location,
                       checkout_location):
    user = subscription1.customer.user

    # We have to have a box checked out to check one in.
    subscription1.tag_location(checkout_location)

    request = apirf.post(
        '/api/v1/tag/',
        {"subscription": subscription1.pk,
         "location": checkin_location.uuid},
        format="json")
    force_authenticate(request, user=user)
    response = CheckinCheckoutView.as_view()(request)

    assert response.status_code == 200
    assert response.data['service'] == checkin_location.service
    assert response.data['available_boxes'] == 1


def test_invalid_checkin(apirf, subscription1, checkin_location):
    user = subscription1.customer.user

    request = apirf.post(
        '/api/v1/tag/',
        {"subscription": subscription1.pk,
         "location": checkin_location.uuid},
        format="json")
    force_authenticate(request, user=user)
    response = CheckinCheckoutView.as_view()(request)

    assert response.status_code == 200
    assert 'service' not in response.data
    assert 'detail' in response.data


def test_valid_checkout(apirf, subscription1, checkout_location):
    user = subscription1.customer.user

    request = apirf.post(
        '/api/v1/tag/',
        {"subscription": subscription1.pk,
         "location": checkout_location.uuid},
        format="json")
    force_authenticate(request, user=user)
    response = CheckinCheckoutView.as_view()(request)

    assert response.status_code == 200
    assert response.data['service'] == checkout_location.service
    assert response.data['available_boxes'] == 0


def test_invalid_checkout(apirf, subscription1, checkout_location):
    user = subscription1.customer.user

    # We have to have a box checked out to cause an error.
    subscription1.tag_location(checkout_location)

    request = apirf.post(
        '/api/v1/tag/',
        {"subscription": subscription1.pk,
         "location": checkout_location.uuid},
        format="json")
    force_authenticate(request, user=user)
    response = CheckinCheckoutView.as_view()(request)

    assert response.status_code == 200
    assert 'service' not in response.data
    assert 'detail' in response.data
