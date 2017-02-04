from .models import EmailAddress, Customer


class CustomerAuthBackend:
    def get_user(self, email):
        try:
            email = EmailAddress.objects.get(address=email)
            return email.customer
        except EmailAddress.DoesNotExist:
            return None

    def authenticate(self, email=None, password=None):
        customer = self.get_user(email)
        if customer and customer.check_password(password):
            return customer

        return None
