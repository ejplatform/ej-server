import pytest
from ej_conversations.mommy_recipes import ConversationRecipes
from ej.testing import UrlTester

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
