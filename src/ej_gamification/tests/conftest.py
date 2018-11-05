import pytest

from ej_users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user('email@server.com', 'password')
