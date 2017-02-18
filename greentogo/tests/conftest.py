import pytest
from core.models import Location, Subscription, Subscriber
from pinax.stripe.models import Plan
from faker import Faker
from datetime import datetime
from django.contrib.auth import get_user_model

from vcr import VCR
import os.path


@pytest.fixture(scope="session")
def faker():
    return Faker()


@pytest.fixture(scope="session")
def vcr():
    return VCR(cassette_library_dir=os.path.join(
        os.path.dirname(__file__), "cassettes"))


my_vcr = vcr()


@pytest.fixture
def checkin_location(db):
    loc = Location(service=Location.CHECKIN)
    loc.save()
    return loc


@pytest.fixture
def checkout_location(db):
    loc = Location(service=Location.CHECKOUT)
    loc.save()
    return loc


@pytest.fixture
def plan1(db):
    plan, _ = Plan.objects.get_or_create(
        stripe_id="1BOX",
        defaults={
            "name": "1 Box",
            "currency": "usd",
            "interval": "year",
            "interval_count": 1,
            "amount": 25.00,
            "metadata": {
                "number_of_boxes": "1"
            }
        })
    return plan


@pytest.fixture
def plan2(db):
    plan, _ = Plan.objects.get_or_create(
        stripe_id="2BOX",
        defaults={
            "name": "2 Boxes",
            "currency": "usd",
            "interval": "year",
            "interval_count": 1,
            "amount": 30.00,
            "metadata": {
                "number_of_boxes": "2"
            }
        })
    return plan


@my_vcr.use_cassette()
@pytest.fixture
def user(db, faker):
    User = get_user_model()
    user = User.objects.create_user(
        faker.user_name, password=faker.password(length=10))
    user.save()
    return user


@pytest.fixture
def subscription1(db, user, plan1):
    subscription = Subscription(
        plan=plan1,
        customer=user.customer,
        quantity=1,
        start=datetime.now(),
        status='active', )
    subscription.save()
    subscription.subscribers.add(user.subscriber)
    return subscription


@pytest.fixture
def subscription2(db, user, plan2):
    subscription = Subscription(
        plan=plan2,
        customer=user.customer,
        quantity=1,
        start=datetime.now(),
        status='active', )
    subscription.save()
    subscription.subscribers.add(user.subscriber)
    return subscription
