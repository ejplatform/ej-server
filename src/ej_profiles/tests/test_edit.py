import pytest
from django.test import Client

from ej_users.models import User


@pytest.fixture
def logged_user(db):
    user = User.objects.create_user('email@server.com', 'password')
    client = Client()
    client.force_login(user)
    return client


class TestEditProfile:
    def test_user_logged_access_profile_url(self, logged_user):
        # post without body with forced login works
        resp = logged_user.post('/login/')
        assert resp.url == '/profile/'

    def test_user_logged_access_edit_profile(self, logged_user):
        resp = logged_user.get('/profile/edit')
        assert resp.url == '/profile/edit/'

    def test_user_not_logged_dont_access_edit_profile(self):
        client = Client()
        resp = client.get('/profile/edit/')
        assert 'login' in resp.url
