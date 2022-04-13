from django.test import Client
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_conversations import create_conversation
from ej_boards.models import Board
from ej_users.models import User
import pytest


class TestEnvironment(ConversationRecipes):
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

    def test_get_environment_statistics(self, logged_admin):
        url = "/profile/boards/environment/"

        user = User.objects.create_user("user1@email.br", "password")
        board = Board.objects.create(slug="board1", owner=user, description="board")
        create_conversation("foo", "conv1", user, board=board)

        response = logged_admin.get(url)
        users_count = response.context["users_count"]
        boards_count = response.context["boards_count"]
        conversations_count = response.context["conversations_count"]

        assert users_count == 2
        assert boards_count == 2
        assert conversations_count == 1

    def test_get_active_recent_boards(self, db, logged_admin):
        user = User.objects.create_user("user1@email.br", "password")
        board = Board.objects.create(slug="board1", owner=user, description="board")
        board_2 = Board.objects.create(slug="board2", owner=user, description="board2")
        Board.objects.create(slug="board3", owner=user, description="board3")

        create_conversation("foo", "conv1", user, board=board)
        create_conversation("foo2", "conv2", user, board=board_2)

        url = "/profile/boards/environment/recent-boards/?boardIsActive=true"

        response = logged_admin.get(url)

        recent_boards = response.context["recent_boards"]
        assert len(recent_boards) == 2
        assert recent_boards[0].slug == "board2"
        assert recent_boards[1].slug == "board1"

    def test_get_all_recent_boards(self, db, logged_admin):
        user = User.objects.create_user("user1@email.br", "password")
        board = Board.objects.create(slug="board1", owner=user, description="board")
        board_2 = Board.objects.create(slug="board2", owner=user, description="board2")
        Board.objects.create(slug="board3", owner=user, description="board3")

        create_conversation("foo", "conv1", user, board=board)
        create_conversation("foo2", "conv2", user, board=board_2)

        url = "/profile/boards/environment/recent-boards/?boardIsActive=false"

        response = logged_admin.get(url)

        recent_boards = response.context["recent_boards"]
        assert len(recent_boards) == 4
        assert recent_boards[0].slug == "board3"
        assert recent_boards[1].slug == "board2"
        assert recent_boards[2].slug == "board1"
        assert recent_boards[3].slug == "admintestcom"
