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
    ]
    owner_urls = [
        '/conversations/conversation/edit/',
        '/conversations/conversation/moderate/',
    ]

    @pytest.fixture
    def data(self, conversation, author_db):
        conversation.author = author_db
        conversation.is_promoted = True
        conversation.save()
