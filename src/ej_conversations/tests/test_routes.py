from django.urls import reverse
import json
import pytest
from django.test import Client
from ej_conversations.mommy_recipes import ConversationRecipes
from ej.testing import UrlTester
from ej_users.models import User
from ej_boards.models import Board

from ej_conversations.routes_comments import comment_url


TEST_DOMAIN = "https://domain.com.br"


class TestRoutes(UrlTester, ConversationRecipes):
    public_urls = ["/conversations/"]
    user_urls = [
        "/board-slug/conversations/1/slug/",
        # '/comments/<id>-<hash>/'
    ]
    admin_urls = ["/board-slug/conversations/add/"]
    owner_urls = ["/board-slug/conversations/1/slug/edit/", "/board-slug/conversations/1/slug/moderate/"]

    def get_data(self, request):
        conversation = request.getfixturevalue("conversation")
        try:
            board = request.getfixturevalue("board")
            board.owner = request.getfixturevalue("author_db")
            conversation.board = board
            conversation.author = board.owner
            conversation.is_promoted = True
            board.save()
            conversation.save()
        except Exception as e:
            pass

    def test_can_view_user_url(self, user_client, comment_db):
        url = comment_url(comment_db)
        response = user_client.get(url)
        assert response.status_code == 200

    def test_add_favorite_board(self, admin_client, root_db):
        user = User.objects.create_user("user1@email.br", "password")
        board_1 = Board.objects.create(slug="board1", owner=user, description="board")
        board_2 = Board.objects.create(slug="board2", owner=root_db, description="board2")

        base_url = reverse("boards:conversation-update-favorite-boards", args=[board_1.slug])
        url = f"{base_url}?updateOption=add"
        admin_client.get(url)

        base_url = reverse("boards:conversation-update-favorite-boards", args=[board_2.slug])
        url = f"{base_url}?updateOption=add"
        admin_client.get(url)

        assert root_db.favorite_boards.get(id=board_1.id) == board_1
        assert root_db.favorite_boards.get(id=board_2.id) == board_2
        assert root_db.favorite_boards.count() == 2

    def test_remove_favorite_board(self, admin_client, root_db):
        user = User.objects.create_user("user1@email.br", "password")
        board_1 = Board.objects.create(slug="board1", owner=user, description="board")
        board_2 = Board.objects.create(slug="board2", owner=root_db, description="board2")

        root_db.favorite_boards.add(board_1)
        root_db.favorite_boards.add(board_2)

        assert root_db.favorite_boards.count() == 2

        base_url = reverse("boards:conversation-update-favorite-boards", args=[board_1.slug])
        url = f"{base_url}?updateOption=remove"
        admin_client.get(url)

        base_url = reverse("boards:conversation-update-favorite-boards", args=[board_2.slug])
        url = f"{base_url}?updateOption=remove"
        admin_client.get(url)

        assert root_db.favorite_boards.count() == 0

    def test_board_is_favorite(self, admin_client, root_db):
        user = User.objects.create_user("user1@email.br", "password")
        board_1 = Board.objects.create(slug="board1", owner=user, description="board")
        board_2 = Board.objects.create(slug="board2", owner=root_db, description="board2")

        root_db.favorite_boards.add(board_1)

        url = reverse("boards:conversation-is-favorite-board", args=[board_1.slug])
        response = admin_client.get(url)
        response_json = json.loads(response.content)
        assert response_json["is_favorite_board"] == True

        url = reverse("boards:conversation-is-favorite-board", args=[board_2.slug])
        response = admin_client.get(url)
        response_json = json.loads(response.content)
        assert response_json["is_favorite_board"] == False
