from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate

from apiv1.views import CheckinCheckoutView
from core.models import Location


def test_no_action(apiclient, subscription1, checkin_location):
    user = subscription1.customer.user
    token, _ = Token.objects.get_or_create(user=user)
    apiclient.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    response = apiclient.post(
        '/api/v1/tag/', {"subscription": subscription1.pk,
                         "location": checkin_location.code},
        format="json"
    )

    assert response.status_code == 400
    assert response.data['data']['action'] == "no_action"


def test_no_location(apiclient, subscription1, checkin_location):
    user = subscription1.customer.user
    token, _ = Token.objects.get_or_create(user=user)
    apiclient.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    response = apiclient.post(
        '/api/v1/tag/', {"action": Location.CHECKIN,
                         "subscription": subscription1.pk},
        format="json"
    )

    assert response.status_code == 400
    assert response.data['data']['location'] == "no_location"


def test_action_location_no_match(apiclient, subscription1, checkin_location):
    user = subscription1.customer.user
    token, _ = Token.objects.get_or_create(user=user)
    apiclient.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    response = apiclient.post(
        '/api/v1/tag/', {
            "action": Location.CHECKOUT,
            "subscription": subscription1.pk,
            "location": checkin_location.code
        },
        format="json"
    )

    assert response.status_code == 400
    assert response.data['data']['action'] == "action_and_location_no_match"


def test_valid_checkin(apiclient, subscription1, checkin_location, checkout_location):
    user = subscription1.customer.user
    token, _ = Token.objects.get_or_create(user=user)
    apiclient.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    # We have to have a box checked out to check one in.
    subscription1.tag_location(checkout_location)

    response = apiclient.post(
        '/api/v1/tag/', {
            "action": Location.CHECKIN,
            "subscription": subscription1.pk,
            "location": checkin_location.code
        },
        format="json"
    )

    assert response.status_code == 200
    assert response.data['data']['service'] == checkin_location.service
    assert response.data['data']['available_boxes'] == 1


def test_invalid_checkin(apiclient, subscription1, checkin_location):
    user = subscription1.customer.user
    token, _ = Token.objects.get_or_create(user=user)
    apiclient.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    response = apiclient.post(
        '/api/v1/tag/', {
            "action": Location.CHECKIN,
            "subscription": subscription1.pk,
            "location": checkin_location.code
        },
        format="json"
    )

    assert response.status_code == 400
    assert response.data['data']['subscription'] == 'no_boxes_out'


def test_valid_checkout(apiclient, subscription1, checkout_location):
    user = subscription1.customer.user
    token, _ = Token.objects.get_or_create(user=user)
    apiclient.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    response = apiclient.post(
        '/api/v1/tag/', {
            "action": Location.CHECKOUT,
            "subscription": subscription1.pk,
            "location": checkout_location.code
        },
        format="json"
    )

    assert response.status_code == 200
    assert response.data['data']['service'] == checkout_location.service
    assert response.data['data']['available_boxes'] == 0


def test_invalid_checkout(apiclient, subscription1, checkout_location):
    user = subscription1.customer.user
    token, _ = Token.objects.get_or_create(user=user)
    apiclient.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    # We have to have a box checked out to cause an error.
    subscription1.tag_location(checkout_location)

    response = apiclient.post(
        '/api/v1/tag/', {
            "action": Location.CHECKOUT,
            "subscription": subscription1.pk,
            "location": checkout_location.code
        },
        format="json"
    )

    assert response.status_code == 400
    assert response.data['data']['subscription'] == 'no_boxes_available'
