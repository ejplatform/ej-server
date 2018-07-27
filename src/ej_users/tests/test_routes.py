import pytest
from django.test import Client
from django.http import HttpResponseRedirect
from ej_users.models import User


@pytest.fixture
def logged_client():
    user = User.objects.create_user('name@server.com', '1234', name='name')
    client = Client()
    client.force_login(user)
    yield client
    user.delete()


@pytest.fixture
def mk_user():
    user = User.objects.create_user('user@user.com', '1234')
    yield user
    user.delete()

class TestRegisterRoute:
    def test_register_route(self, db):
        client = Client()
        response = client.post('/register/', data={'name': 'something'})
        assert response.status_code == 200

    def test_register_valid_fields(self, db):
        client = Client()
        response = client.post('/register/', data={
            'name': "Turanga Leela",
            'email': "leela@example.com",
            'password': "pass123",
            'password_confirm': 'pass123'
        })
        assert response.status_code == 302
        assert isinstance(response, HttpResponseRedirect)
        assert response.url == '/'

    def test_register_logged_user_route(self, db, logged_client):
        client = logged_client
        response = client.post('/register/', data={'name': 'something'})
        assert response.status_code == 200


class TestLoginRoute:
    def test_login_route(self, db):
        client = Client()
        response = client.post('/login/', data={'email': 'email'})
        assert response.status_code == 200

    def test_login_logged_user_route(self, db, logged_client):
        client = logged_client
        response = client.post('/login/', data={'name': 'something'})
        assert response.status_code == 200

    def test_login_user_route(self, db, mk_user):
        user = mk_user
        client = Client()
        response = client.post('/login/', data={'email': 'user@user.com', 'password': '1234'})
        assert response.status_code == 302
        assert isinstance(response, HttpResponseRedirect)
        assert response.url == '/'

class TestLogoutRoute:
    def test_logout_anonymous_user_route(self):
        client = Client()
        response = client.post('/logout/')
        assert response.status_code == 302


class TestRecoverPasswordRoute:
    def test_anonymous_user_recover_password(self, db):
        client = Client()
        response = client.post('/profile/recover-password/')
        assert response.status_code == 200


class TestResetPasswordRoute:
    def test_anonymous_user_reset_password(self, db):
        client = Client()
        response = client.post('/profile/reset-password/')
        assert response.status_code == 302


class TestRemoveProfileRoute:
    def test_anonymous_user_remove_profile(self, db):
        client = Client()
        response = client.post('/profile/remove/')
        assert response.status_code == 302


class TestFavoriteConversationRoute:
    def test_anonymous_user_remove_profile(self, db):
        client = Client()
        response = client.post('/profile/remove/')
        assert response.status_code == 302
