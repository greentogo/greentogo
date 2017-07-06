from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate

from apiv1.views import CheckinCheckoutView
from core.models import Subscription


def test_valid_change(apiclient, subscription1, plan2):
    assert False, "conftest is not creating all the objects we need"
    # user = subscription1.customer.user
    # token, _ = Token.objects.get_or_create(user=user)
    # apiclient.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    # url = '/api/v1/subscriptions/{}/'.format(subscription1.stripe_id)
    # response = apiclient.put(
    #     url,
    #     {"stripe_id": plan2.stripe_id},
    #     format="json"
    # )

    # assert response.status_code == 200
    # assert response.data['data']['updated'] == plan2.stripe_id
