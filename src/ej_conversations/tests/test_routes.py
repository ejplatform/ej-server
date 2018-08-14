import pytest
from ej.testing import UrlTester
from ej_conversations.mommy_recipes import ConversationRecipes


class TestRoutes(UrlTester, ConversationRecipes):
    public_urls = [
        '/conversations/',
        '/conversations/conversation/',
    ]
    login_urls = [
        '/conversations/add/',
        '/conversations/conversation/info',
    ]
    owner_urls = [
        '/conversations/conversation/edit/',
    ]

    @pytest.fixture
    def data(self, conversation, author_db):
        conversation.author = author_db
        conversation.save()
