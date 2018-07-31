import pytest

from ej.testing import UrlTester
from ej_boards.mommy_recipes import BoardRecipes


class TestBoards(BoardRecipes, UrlTester):
    public_urls = [
        # /board-slug/ will not be tested because it is handled by the
        # middleware and thus disabled in the test client,
        # '/board-slug/conversations/',
        # '/board-slug/conversations/conversation-slug/',
    ]
    user_urls = []
    owner_urls = [
        # '/board-slug/conversations/add/',
        # '/board-slug/conversations/conversation-slug/edit/',
    ]

    @pytest.fixture
    def data(self, board, conversation, author_db):
        board.owner = conversation.author = author_db
        board.save()
        conversation.save()
        board.add_conversation(conversation)
