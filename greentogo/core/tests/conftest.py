import pytest
from core.models import Location, SubscriptionPlan, Subscription, Subscriber
from faker import Faker
from datetime import datetime
from django.contrib.auth import get_user_model


@pytest.fixture(scope="session")
def faker():
    return Faker()


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
def subscription_plan1(db):
    plan, _ = SubscriptionPlan.objects.get_or_create(
        code="1BOX", defaults={"description": "1 Box",
                               "number_of_boxes": 1})
    return plan


@pytest.fixture
def subscription_plan2(db):
    plan, _ = SubscriptionPlan.objects.get_or_create(
        code="2BOX", defaults={"description": "2 Boxes",
                               "number_of_boxes": 2})
    return plan


@pytest.fixture
def subscription_plan_unlimited(db):
    plan, _ = SubscriptionPlan.objects.get_or_create(
        code="UNLIMIT", defaults={"description": "Unlimited"})
    return plan


@pytest.fixture
def user(db, faker):
    User = get_user_model()
    user = User.objects.create_user(
        faker.user_name, password=faker.password(length=10))
    user.save()
    return user


@pytest.fixture
def subscriber(db, user):
    return user.subscriber


@pytest.fixture
def subscription1(db, subscriber, subscription_plan1):
    subscription = Subscription(
        plan=subscription_plan1, admin=subscriber, started_on=datetime.now())
    subscription.save()
    subscription.subscriber_set.add(subscriber)
    return subscription


@pytest.fixture
def subscription2(db, subscriber, subscription_plan2):
    subscription = Subscription(
        plan=subscription_plan2, admin=subscriber, started_on=datetime.now())
    subscription.save()
    subscription.subscriber_set.add(subscriber)
    return subscription
