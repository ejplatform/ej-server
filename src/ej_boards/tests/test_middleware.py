from django.test import TestCase
from django.test.client import Client
import pytest

from ..models import Board
from ej_users.models import User


class BoardMiddlewareTestCase(TestCase):

  def setUp(self):
    user = User.objects.create_user('foo@server.com', 'password')
    user.save()
    board = Board.objects.create(owner=user, 
                                 title='my board', 
                                 slug='my-board',
                                 custom_domain='lojasamericanas.com')
    board.save()

  def test_redirect_to_board_based_on_domain(self):
    client = Client()
    response = client.get('/home', **{'HTTP_HOST': 'lojasamericanas.com'})
    self.assertEqual(response.url, '/my-board/conversations')

