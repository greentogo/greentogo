import os.path
from datetime import datetime

from django.contrib.auth import get_user_model

import pytest
from faker import Faker
from vcr import VCR

from core.models import Location, Plan, Subscription


@pytest.fixture(scope="session")
def faker():
    return Faker()


@pytest.fixture(scope="session")
def vcr():
    return VCR(cassette_library_dir=os.path.join(os.path.dirname(__file__), "cassettes"))


my_vcr = vcr()


@my_vcr.use_cassette()
@pytest.fixture
def checkin_location(db):
    loc = Location(
        service=Location.CHECKIN,
        name="Test Checkin Location",
        address="119 Orange St, Durham, NC 27701"
    )
    loc.save()
    return loc


@my_vcr.use_cassette()
@pytest.fixture
def checkout_location(db):
    loc = Location(
        service=Location.CHECKOUT,
        name="Test Checkout Location",
        address="119 Orange St, Durham, NC 27701"
    )
    loc.save()
    return loc


@my_vcr.use_cassette()
@pytest.fixture
def user(db, faker):
    User = get_user_model()
    user = User.objects.create_user(faker.user_name(), password=faker.password(length=10))
    user.save()
    return user


@my_vcr.use_cassette()
@pytest.fixture
def plan1(db):
    plan1 = Plan.objects.create(name="1 Box", amount=0, number_of_boxes=1, stripe_id="TEST1")
    return plan1


@my_vcr.use_cassette()
@pytest.fixture
def plan2(db):
    plan1 = Plan.objects.create(name="2 Boxes", amount=0, number_of_boxes=2, stripe_id="TEST2")
    return plan1


@my_vcr.use_cassette()
@pytest.fixture
def subscription1(db, user, plan1):
    subscription = Subscription.objects.create(plan=plan1, user=user)
    return subscription


@my_vcr.use_cassette()
@pytest.fixture
def subscription2(db, user, plan2):
    subscription = Subscription.objects.create(plan=plan2, user=user)
    return subscription
