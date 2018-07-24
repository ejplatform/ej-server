import pytest

from ej_conversations import create_conversation
from ej_users.models import User


class TestUserManager:
    def test_can_create_and_fetch_simple_user(self, db):
        user = User.objects.create_user('name@server.com', '1234', name='name')
        assert user.name == 'name'
        assert user.password != '1234'
        assert User.objects.get_by_email('name@server.com') == user

    @pytest.fixture
    def conversation(self):
        user = User.objects.create_user('c@server.com', '1234', name='c')
        return create_conversation('favorite?', 'conversation', user)

    @pytest.fixture
    def user(self):
        return User.objects.create_user('favorite@server.com', '1234', name='usr')

    def test_user_favorite_conversation(self, db, conversation, user):
        user.favorite_conversations.add(conversation)
        favorite_conversations = user.favorite_conversations
        assert favorite_conversations.filter(id=conversation.id).exists()

    def test_user_update_favorite_conversation_status_add(self, db, conversation, user):
        user.update_favorite_conversation_status(conversation)
        favorite_conversations = user.favorite_conversations
        assert favorite_conversations.filter(id=conversation.id).exists()

    def test_user_update_favorite_conversation_status_remove(self, db, conversation, user):
        user.favorite_conversations.add(conversation)
        user.update_favorite_conversation_status(conversation)
        favorite_conversations = user.favorite_conversations
        assert not favorite_conversations.filter(id=conversation.id).exists()
