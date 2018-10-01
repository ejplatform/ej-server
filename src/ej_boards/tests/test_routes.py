from django.test import TestCase, Client

from ej.testing import UrlTester
from ej_users.models import User


class TestRoutes(UrlTester):
    public_urls = [
    ]
    login_urls = [
        '/ej_boards/',
        '/ej_boards/add/',
        '/ej_boards/board/edit/',
    ]
    owner_urls = [
    ]


class TestBoardRoutes(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('name@server.com', '1234', name='name')
        client = Client()
        client.force_login(self.user)
        self.logged_client = client

    def test_list_profile_boards(self):
        pass

    def test_list_profile_board_anonymous_user(self):
        client = Client()
        response = client.post('/profile/boards/')
        self.assertRedirects(response, '/login/?next=/profile/boards/', 302, 200)

    def test_create_board(self):
        pass

    def test_create_board_anonymous_user(self):
        client = Client()
        response = client.post('/profile/boards/add/')
        self.assertRedirects(response, '/login/?next=/profile/boards/add/', 302, 200)
