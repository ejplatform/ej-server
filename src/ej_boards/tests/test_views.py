import pytest

from ej.testing import UrlTester
from ej_conversations.mommy_recipes import ConversationRecipes


class TestBoards(UrlTester, ConversationRecipes):
    public_urls = [
        # /board-slug/ will not be tested because it is handled by the
        # middleware and thus disabled in the test client,
        '/board-slug/conversations/',
        # '/board-slug/conversations/conversation-slug/',
    ]
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
