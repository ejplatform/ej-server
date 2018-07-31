import pytest
from django.test import Client
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.test import TestCase

from ej_users.models import User


@pytest.fixture
def logged_client(db):
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


class TestLoginRoute:
    def test_login_route(self, db):
        client = Client()
        response = client.post('/login/', data={'email': 'email'})
        assert response.status_code == 200

    def test_login_logged_user_route(self, logged_client):
        client = logged_client
        response = client.post('/login/', data={'name': 'something'})
        assert response.url == '/profile/'

    def test_login_user_route(self, db, mk_user):
        user = mk_user
        client = Client()
        assert '_auth_user_id' not in client.session
        response = client.post('/login/', data={'email': 'user@user.com', 'password': '1234'})

        assert response.status_code == 302
        assert isinstance(response, HttpResponseRedirect)
        assert response.url == '/'
        assert int(client.session['_auth_user_id']) == user.pk


class TestLogoutRoute:
    def test_logout_anonymous_user_route(self):
        client = Client()
        response = client.post('/logout/')
        assert response.status_code == 302

    def test_logout_with_get(self):
        client = Client()
        response = client.get('/logout/')

        assert isinstance(response, HttpResponseServerError)
        assert response.status_code == 500
        assert response.content.decode("utf-8") == 'cannot logout using a GET'

    def test_logout_logged_user(self, logged_client):
        client = logged_client
        assert '_auth_user_id' in client.session
        client.post('/logout/')
        assert '_auth_user_id' not in client.session


class TestRegisterRoute(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('name@server.com', '1234', name='name')
        client = Client()
        client.force_login(self.user)
        self.logged_client = client

    def tearDown(self):
        self.user.delete()

    def test_register_route(self):
        client = Client()
        response = client.post('/register/', data={'name': 'something'})

        self.assertEqual(response.status_code, 200)

    def test_register_valid_fields(self):
        client = Client()
        assert '_auth_user_id' not in client.session
        response = client.post('/register/', data={
            'name': "Turanga Leela",
            'email': "leela@example.com",
            'password': "pass123",
            'password_confirm': 'pass123'
        }, follow=True)
        user_pk = User.objects.get(email="leela@example.com").pk
        self.assertEqual(int(client.session['_auth_user_id']), user_pk)
        self.assertRedirects(response, '/conversations/', 302, 200)


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


class TestFavoriteConversationRoute:
    def test_anonymous_user_favorite_conversations(self, db):
        client = Client()
        response = client.post('/profile/favorites/')
        assert response.status_code == 302
