from django.contrib.auth.models import User


def get_user_mapping():
    """
    A function that will return a dict of user id and username.
    """
    users = User.objects.all().values('id', 'username')
    user_mapping = {user['id']: user['username'] for user in users}
    return user_mapping
