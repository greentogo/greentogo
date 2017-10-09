import pytest

from apiv1.serializers import CheckinCheckoutSerializer
from core.models import Location

pytestmark = pytest.mark.django_db


def location_must_be_valid():
    serializer = CheckinCheckoutSerializer(data={"location": "BUTT"})
    assert not serializer.is_valid()
    assert 'Location does not exist.' in serializer.errors['location']


def test_action_must_be_valid():
    serializer = CheckinCheckoutSerializer(data={"action": "doit"})
    assert not serializer.is_valid()
    assert '"doit" is not a valid choice.' in serializer.errors['action']


def test_checkin_only_at_checkin_location(checkout_location, subscription1):
    serializer = CheckinCheckoutSerializer(
        data={
            "subscription": subscription1.pk,
            "action": Location.CHECKIN,
            "location": checkout_location.code,
        }
    )
    assert not serializer.is_valid()
    assert "Invalid action for this location." in serializer.errors['non_field_errors']


def test_checkout_only_at_checkout_location(checkin_location, subscription1):
    serializer = CheckinCheckoutSerializer(
        data={
            "subscription": subscription1.pk,
            "action": Location.CHECKOUT,
            "location": checkin_location.code,
        }
    )
    assert not serializer.is_valid()
    assert "Invalid action for this location." in serializer.errors['non_field_errors']


def test_valid_action(checkin_location, subscription1):
    serializer = CheckinCheckoutSerializer(
        data={
            "subscription": subscription1.pk,
            "action": Location.CHECKIN,
            "location": checkin_location.code
        }
    )
    assert serializer.is_valid()
