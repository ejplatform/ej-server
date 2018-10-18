import pytest
from django.test import TestCase, Client

from ej_conversations.mommy_recipes import ConversationRecipes
from ej_boards.models import Board
from ej_boards.mommy_recipes import BoardRecipes
from ej.testing import UrlTester
from ej_users.models import User


class TestRoutes(UrlTester, BoardRecipes, ConversationRecipes):
    public_urls = [
        '/board-slug/conversations/',
        '/board-slug/conversations/conversation/'
    ]
    login_urls = [
        '/ej_boards/',
        '/ej_boards/add/',
        '/ej_boards/board/edit/',
        '/profile/boards/add/',
        '/profile/boards/'
    ]
    owner_urls = [
        '/board-slug/edit/',
        '/board-slug/conversations/conversation/edit/',
        '/board-slug/conversations/conversation/moderate/',
        '/board-slug/conversations/conversation/stereotypes/',
        '/board-slug/conversations/conversation/stereotypes/add/'
    ]

    @pytest.fixture
    def data(self, conversation, author_db, board):
        board.owner = author_db
        board.save()
        conversation.author = author_db
        conversation.save()
        print(author_db.profile)
        board.add_conversation(conversation)


class TestBoardRoutes(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('name@server.com', '1234', name='name')
        client = Client()
        client.force_login(self.user)
        self.logged_client = client

    def test_list_profile_boards(self):
        client = self.logged_client
        response = client.get('/profile/boards/')
        self.assertTrue(response.status_code, 200)

    def test_list_profile_board_anonymous_user(self):
        client = Client()
        response = client.get('/profile/boards/')
        self.assertRedirects(response, '/login/?next=/profile/boards/', 302, 200)

    def test_create_board(self):
        client = self.logged_client
        data = {'slug': 'slug',
                'title': 'new title',
                'description': 'description '}
        response = client.post('/profile/boards/add/', data=data)
        self.assertRedirects(response, '/slug/', 302, 200)

    def test_create_invalid_board(self):
        client = self.logged_client
        data = {'slug': 's', 'title': 'title', 'description': ''}
        response = client.post('/profile/boards/add/', data=data)
        self.assertTrue(response.status_code, 200)

    def test_get_create_board(self):
        client = self.logged_client
        response = client.get('/profile/boards/add')
        self.assertTrue(response.status_code, 200)

    def test_create_board_anonymous_user(self):
        client = Client()
        response = client.get('/profile/boards/add/')
        self.assertRedirects(response, '/login/?next=/profile/boards/add/', 302, 200)

    def test_edit_board_anonymous_user(self):
        client = Client()
        Board.objects.create(slug='slug1', title='title1', owner=self.user)
        response = client.get('/slug1/edit/')
        self.assertTrue(response.status_code, 404)

    def test_edit_board_logged_user(self):
        client = self.logged_client
        Board.objects.create(slug='slug1', title='title1', owner=self.user)
        data = {'slug': 'slug1', 'title': 'new title'}
        response = client.post('/slug1/edit/', data=data)
        self.assertRedirects(response, '/slug1/', 302, 200)

    def test_edit_invalid_board_logged_user(self):
        client = self.logged_client
        Board.objects.create(slug='slug1', title='title1', owner=self.user)
        data = {'slug': 'slug1'}
        response = client.post('/slug1/edit/', data=data)
        self.assertTrue(response.status_code, 200)
