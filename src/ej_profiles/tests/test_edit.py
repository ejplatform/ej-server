import pytest
from django.test import Client
from django.test import TestCase

from ej_users.models import User


@pytest.fixture
def logged_user(db):
    user = User.objects.create_user('email@server.com', 'password')
    client = Client()
    client.force_login(user)
    return client


class TestEditProfile:
    @pytest.mark.logged
    def test_user_logged_access_profile_url(self, logged_user):
        # post without body with forced login works
        resp = logged_user.post('/login/')
        assert resp.url == '/profile/'
