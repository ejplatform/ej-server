import pytest
from django.http import HttpResponseRedirect
from django.test import Client
from django.test import TestCase

from ej.testing import UrlTester
from ej_users.models import User


@pytest.fixture
def logged_client(db):
    user = User.objects.create_user('name@server.com', '1234', name='name')
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def mk_user():
    return User.objects.create_user('user@user.com', '1234')


class TestRoutes(UrlTester):
    public_urls = [
        '/register/',
        '/login/',
        '/profile/recover-password/',
    ]
    user_urls = [
        # '/logout/', -- returns error 500, so we use specific tests
        '/profile/reset-password/',
        '/profile/remove/',
        '/profile/favorites/',
    ]

    # TODO test profile/api-key/

    def test_logout(self, logged_client):
        client = logged_client
        assert '_auth_user_id' in client.session
        client.post('/logout/')
        assert '_auth_user_id' not in client.session

    def test_logout_fails_with_anonymous_user(self, client):
        response = client.post('/logout/')
        assert response.status_code == 500

    def test_logout_fails_with_get(self, client):
        response = client.get('/logout/')
        assert response.status_code == 500


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


class TestRegisterRoute(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('name@server.com', '1234', name='name')
        client = Client()
        client.force_login(self.user)
        self.logged_client = client

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
        self.assertRedirects(response, '/home/', 302, 200)
