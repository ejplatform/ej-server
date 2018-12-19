from django.test import TestCase
from django.test.client import Client
import pytest
import django

from ..models import Board
from ej_users.models import User


class BoardMiddlewareTestCase(TestCase):

    def setUp(self):
        django.conf.settings.ALLOWED_HOSTS.append('.ejplatform.org')
        django.setup()

    def test_redirect_to_board_based_on_sub_domain(self):
        user = User.objects.create_user('foo@server.com', 'password')
        user.save()
        board = Board.objects.create(owner=user,
                                    title='my board',
                                    slug='my-board',
                                    sub_domain='lojasamericanas.ejplatform.org')
        client = Client()
        response = client.get('/home/', **{'HTTP_HOST': 'lojasamericanas.ejplatform.org'})
        self.assertEqual(response.url, '/my-board/conversations')

    def test_redirect_to_home_if_board_not_exists(self):
        user = User.objects.create_user('foo@server.com', 'password')
        user.save()
        board = Board.objects.create(owner=user,
                                    title='my board',
                                    slug='my-board',
                                    sub_domain='lojasamericanas.ejplatform.org')
        client = Client()
        response = client.get('/home/', **{'HTTP_HOST': 'bancodobrasil.ejplatform.org'})
        self.assertEqual(response.status_code, 200)

    def test_alaways_redirect_to_board_for_sub_domain(self):
        user = User.objects.create_user('foo@server.com', 'password')
        user.save()
        board = Board.objects.create(owner=user,
                                    title='my board',
                                    slug='my-board-2',
                                    sub_domain='lojasamericanas.ejplatform.org')
        client = Client()
        response = client.get('/conversations/', **{'HTTP_HOST': 'lojasamericanas.ejplatform.org'})
        self.assertEqual(response.url, '/my-board-2/conversations')


    def test_alaways_redirect_to_board_for_sub_domain_when_logged(self):
        user = User.objects.create_user('foo@server.com', 'password')
        user.save()
        board = Board.objects.create(owner=user,
                                    title='my board',
                                    slug='my-board-2',
                                    sub_domain='lojasamericanas.ejplatform.org')
        client = Client()
        client.force_login(user)
        response = client.get('/home/', **{'HTTP_HOST': 'lojasamericanas.ejplatform.org'})
        self.assertEqual(response.url, '/my-board-2/conversations')
        self.assertEqual(response.status_code, 302)
        response = client.get('/conversations/', **{'HTTP_HOST': 'lojasamericanas.ejplatform.org'})
        self.assertEqual(response.url, '/my-board-2/conversations')
        self.assertEqual(response.status_code, 302)

    def test_not_apply_middleware_for_domain(self):
        user = User.objects.create_user('foo@server.com', 'password')
        user.save()
        board = Board.objects.create(owner=user,
                                    title='my board',
                                    slug='my-board-2',
                                    sub_domain='')
        client = Client()
        client.force_login(user)
        response = client.get('/home/', **{'HTTP_HOST': 'ejplatform.org'})
        self.assertEqual(response.status_code, 200)
        response = client.get('/conversations/', **{'HTTP_HOST': 'ejplatform.org'})
        self.assertEqual(response.status_code, 200)
