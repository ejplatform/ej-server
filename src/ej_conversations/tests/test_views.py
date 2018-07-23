import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import RequestFactory

from ej_conversations import create_conversation
from ej_conversations.models import Conversation
from ej_conversations.models.comment import votes_counter
from ej_conversations.routes import base, admin
from ej_users.models import User


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def post_request(request_factory):
    request = request_factory.post('')
    request.user = AnonymousUser()
    return request


@pytest.fixture
def get_request(request_factory):
    request = request_factory.get('')
    request.user = AnonymousUser()
    return request


@pytest.fixture
def get_request_with_user(request_factory, user):
    request = request_factory.get('/testboard/')
    request.user = user
    return request


@pytest.fixture
def user(db):
    user = User.objects.create_user('email@server.com', 'password')
    user.board_name = 'testboard'
    user.save()
    return user


@pytest.fixture
def conversation(db, user):
    return create_conversation(text='test', title='title', author=user)


@pytest.fixture
def comment(db, conversation, user):
    return conversation.create_comment(user, 'content', 'approved')


class TestConversationBase:
    def test_get_all_conversations_of_another_user(self, get_request, user, conversation, db):
        response = base.conversation_list(get_request, user)
        assert response.get('conversations')._obj.model is Conversation
        assert response.get('can_add_conversation') is False
        assert response.get('owner') is user
        assert response.get('add_link') is ''

    def test_get_all_conversations_of_user_board(self, get_request_with_user, user, conversation, db):
        response = base.conversation_list(get_request_with_user)
        assert response.get('conversations')._obj.model is Conversation
        assert response.get('owner') is None
        assert str(response.get('add_link')) is not None

    def test_get_all_promoted_conversations(self, get_request, user, conversation, db):
        response = base.conversation_list(get_request)
        assert response.get('conversations')._obj.model is Conversation
        assert response.get('can_add_conversation') is False
        assert response.get('owner') is None
        assert response.get('add_link') is ''

    def test_conversation_detail_without_being_author(self, get_request, user, conversation, db):
        response = base.detail(get_request, conversation)
        assert isinstance(response.get('conversation'), Conversation)
        assert response.get('comment') is None
        assert response.get('owner') is None
        assert response.get('edit_perm') is False
        assert response.get('can_comment') is False
        assert response.get('remainig_comments') is None
        assert str(response.get('login_link')) is not None

    def test_conversation_detail_being_author(self, get_request_with_user, user, conversation, db):
        response = base.detail(get_request_with_user, conversation, user)
        assert isinstance(response.get('conversation'), Conversation)
        assert response.get('comment') is None
        assert response.get('owner') is user
        assert response.get('edit_perm') is True
        assert response.get('can_comment') is True
        assert response.get('remainig_comments') is None
        assert str(response.get('login_link')) is not None

    def test_vote_in_comment(self, request_factory, conversation, comment, db):
        request = request_factory.post('', {'action': 'vote', 'vote': 'agree'})
        user = User.objects.create_user('user@server.com', 'password')
        request.user = user
        conversation.comment = comment
        conversation.save()
        response = base.detail(request, conversation)
        assert votes_counter(response.get('comment')) == 1


class TestConversationAdmin:
    def test_cannot_create_conversation_for_another_user(self, post_request, user):
        with pytest.raises(Http404):
            admin.create(post_request, user)
