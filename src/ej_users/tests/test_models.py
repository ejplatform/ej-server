import pytest
from django.core.exceptions import ValidationError

from ej_users.models import User


class TestUserManager:
    def test_can_create_and_fetch_simple_user(self, db):
        user = User.objects.create_user('my_user', 'name@server.com', '1234', name='name')
        assert user.name == 'name'
        assert user.password != '1234'
        assert User.objects.get_by_email_or_username('my_user') == user
        assert User.objects.get_by_email_or_username('name@server.com') == user

    def test_cannot_create_user_with_conflicting_username(self, db):
        # Blacklisted names
        with pytest.raises(ValidationError):
            print(User.objects.create_user('me', 'me@server.com', '1234', name='name'))

        # Conflict with other urls
        with pytest.raises(ValidationError):
            print(User.objects.create_user('conversations', 'me@server.com', '1234', name='name'))
