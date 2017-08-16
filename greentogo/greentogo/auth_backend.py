from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class AuthBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        user = UserModel.objects.filter(username=username).first() or \
               UserModel.objects.filter(email=username).first()

        if user and getattr(user, 'is_active', False) and user.check_password(password):
            return user

        return None
