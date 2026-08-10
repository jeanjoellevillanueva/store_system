from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailOrLegacyUsernameBackend(ModelBackend):
    """
    Authenticate verified users by email, case-insensitively

    A username is accepted only for a legacy user whose email is still blank.
    This preserves enrollment without allowing verified users to bypass the
    email-login requirement.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = (kwargs.get('email') or username or '').strip()

        if not identifier or password is None:
            return None

        user = User.objects.filter(email__iexact=identifier).first()

        if user is None:
            user = User.objects.filter(
                username=identifier,
                email='',
            ).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None