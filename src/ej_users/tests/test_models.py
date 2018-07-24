import pytest

from ej_conversations import create_conversation
from ej_users.models import User


class TestUserManager:
    def test_can_create_and_fetch_simple_user(self, db):
        user = User.objects.create_user('name@server.com', '1234', name='name')
        assert user.name == 'name'
        assert user.password != '1234'
        assert User.objects.get_by_email('name@server.com') == user
