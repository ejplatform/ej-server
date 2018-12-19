from django.test import TestCase
from django.test.client import Client
import pytest
import django

from ..models import User
from ej_boards.models import Board


class UserMiddlewareTestCase(TestCase):

    def setUp(self):
        django.conf.settings.ALLOWED_HOSTS.append('.ejplatform.org')
        django.setup()

    def test_not_redirect_to_domain_for_login_without_next(self):
        user = User.objects.create_user('foo@server.com', 'password')
        user.save()
        client = Client()
        response = client.get('/login/', **{'HTTP_HOST': 'lojasamericanas.ejplatform.org'})
        self.assertEqual(response.status_code, 200)

    def test_sub_domain_redirect_url(self):
        user = User.objects.create_user('foo@server.com', 'password')
        user.save()
        Board.objects.create(owner=user,
                                title='my board',
                                slug='my-board-2',
                                sub_domain='lojasamericanas.ejplatform.org')
        client = Client()
        response = client.get('/login/?next=https://lojasamericanas.ejplatform.org/my-board-2/conversations/',
                                **{'HTTP_HOST': 'lojasamericanas.ejplatform.org'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://ejplatform.org/login/?next=https://lojasamericanas.ejplatform.org/my-board-2/conversations/')


    def test_not_redirect_when_access_from_domain_with_next(self):
        user = User.objects.create_user('foo@server.com', 'password')
        user.save()
        client = Client()
        response = client.get('/login/', **{'HTTP_HOST': 'ejplatform.org'})
        response = client.get('/login/?next=/my-board-2/conversations/',**{'HTTP_HOST': 'ejplatform.org'})
        self.assertEqual(response.status_code, 200)
