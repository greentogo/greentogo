import pytest


@pytest.fixture
def apirf():
    from rest_framework.test import APIRequestFactory
    return APIRequestFactory()


@pytest.fixture
def apiclient():
    from rest_framework.test import APIClient
    return APIClient()
