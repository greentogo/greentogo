from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate

from apiv1.views import CheckinCheckoutView
from core.models import Location


def test_no_action(apiclient, subscription1, checkin_location):
    user = subscription1.user
    token, _ = Token.objects.get_or_create(user=user)
    apiclient.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    response = apiclient.post(
        '/api/v1/tag/', {"subscription": subscription1.pk,
                         "location": checkin_location.code},
        format="json"
    )

    print(response.data)
    assert response.status_code == 400
    assert "This field is required." in response.data['data']['action']


def test_no_location(apiclient, subscription1, checkin_location):
    user = subscription1.user
    token, _ = Token.objects.get_or_create(user=user)
    apiclient.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    response = apiclient.post(
        '/api/v1/tag/', {"action": Location.CHECKIN,
                         "subscription": subscription1.pk},
        format="json"
    )

    assert response.status_code == 400
    assert "This field is required." in response.data['data']['location']


def test_action_location_no_match(apiclient, subscription1, checkin_location):
    user = subscription1.user
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
    assert "Invalid action for this location." in response.data['data']['non_field_errors']


def test_valid_checkin(apiclient, subscription1, checkin_location, checkout_location):
    user = subscription1.user
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
    assert response.data['data'][0]['service'] == checkin_location.service
    assert response.data['data'][0]['available_boxes'] == 1


def test_valid_checkin_multiple_boxes(
    apiclient, subscription2, checkin_location, checkout_location
):
    user = subscription2.user
    token, _ = Token.objects.get_or_create(user=user)
    apiclient.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    # We have to have a box checked out to check one in.
    subscription2.tag_location(checkout_location, 2)

    response = apiclient.post(
        '/api/v1/tag/', {
            "action": Location.CHECKIN,
            "subscription": subscription2.pk,
            "location": checkin_location.code,
            "number_of_boxes": 2
        },
        format="json"
    )

    assert response.status_code == 200
    assert response.data['data'][0]['service'] == checkin_location.service
    assert response.data['data'][0]['available_boxes'] == 2


def test_invalid_checkin(apiclient, subscription1, checkin_location):
    user = subscription1.user
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
    assert response.data['data']['subscription'] == 'Not enough boxes checked out.'


def test_valid_checkout(apiclient, subscription1, checkout_location):
    user = subscription1.user
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
    assert response.data['data'][0]['service'] == checkout_location.service
    assert response.data['data'][0]['available_boxes'] == 0


def test_valid_checkout_multiple_boxes(apiclient, subscription2, checkout_location):
    user = subscription2.user
    token, _ = Token.objects.get_or_create(user=user)
    apiclient.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    response = apiclient.post(
        '/api/v1/tag/', {
            "action": Location.CHECKOUT,
            "subscription": subscription2.pk,
            "location": checkout_location.code,
            "number_of_boxes": 2
        },
        format="json"
    )

    assert response.status_code == 200
    assert response.data['data'][0]['service'] == checkout_location.service
    assert response.data['data'][0]['available_boxes'] == 0


def test_invalid_checkout(apiclient, subscription1, checkout_location):
    user = subscription1.user
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
    assert response.data['data']['subscription'] == 'Not enough boxes available for checkout.'
