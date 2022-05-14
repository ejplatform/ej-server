from django.test import Client
import pytest
from ej_users.models import User
from ej_boards.models import Board
from ej_conversations.models import Conversation
from ej_conversations.mommy_recipes import ConversationRecipes


class TestSignaturesViews(ConversationRecipes):
    @pytest.fixture
    def admin_user(self, db):
        admin_user = User.objects.create_superuser("admin@test.com", "pass")
        admin_user.save()
        return admin_user

    @pytest.fixture
    def logged_admin(self, admin_user):
        client = Client()
        client.force_login(admin_user)
        return client

    @pytest.fixture
    def user(self, db, logged_admin):
        user = User.objects.create_user(email="user1@email.br", password="password")
        user.save()
        board = Board.objects.create(slug="board1", owner=user, description="board")
        board.owner = user
        board.save()
        conversation = Conversation.objects.create(author=user, board=board)
        conversation.save()
        return user

    def test_signatures_list(self, db, board, logged_admin, user):
        client = Client()
        client.login(email=user.email, password="password")
        response = client.get(f"/{board.slug}/signatures/")
        assert response.status_code == 200
