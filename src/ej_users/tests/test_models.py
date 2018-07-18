import pytest
from django.core.exceptions import ValidationError

from ej_users.models import User, username
from ej_conversations import create_conversation


class TestUserManager:
    def test_can_create_and_fetch_simple_user(self, db):
        user = User.objects.create_user('my_user', 'name@server.com', '1234', name='name')
        assert user.name == 'name'
        assert user.password != '1234'
        assert User.objects.get_by_email_or_username('my_user') == user
        assert User.objects.get_by_email_or_username('name@server.com') == user

    def test_cannot_create_user_with_conflicting_username(self, db):
        # Blacklisted names
        with pytest.raises(ValidationError):
            print(User.objects.create_user('me', 'me@server.com', '1234', name='name'))

        # Conflict with other urls
        with pytest.raises(ValidationError):
            print(User.objects.create_user('conversations', 'me@server.com', '1234', name='name'))

    @pytest.fixture
    def conversation(self):
        user = User.objects.create_user('c', 'c@server.com', '1234', name='c')
        conversation = create_conversation('favorite?', 'conversation', user)
        yield conversation
        conversation.delete()

    @pytest.fixture
    def user(self):
        user = User.objects.create_user('usr', 'favorite@server.com', '1234', name='usr')
        yield user
        user.delete()

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

    def test_can_generate_username_with_same_name(self, db):
        username_firstname = username('Name Name', 'name@server.com')
        user = User.objects.create_user(username_firstname, 'name@server.com', '123')
        assert user.username == 'name'

        username_email = username('Name Name', 'name2@server.com')
        user = User.objects.create_user(username_email, 'name2@server.com', '123')
        assert user.username == 'name2'

        username_by_name_combination = username('Name Name', 'name@server.com')
        user = User.objects._create_user(username_by_name_combination, 'name@server.com', '123')
        assert user.username == 'namename'

        username_by_email = username('Name Name', 'name@server.com')
        user = User.objects.create_user(username_by_email, 'name@server.com', '123')
        assert user.username == 'name1'
