from django.contrib.auth import authenticate


def test_customer_auth_works(customer):
    email = customer.emailaddress_set.first().address
    authorized_user = authenticate(email=email, password=customer.password)
    assert customer == authorized_user
