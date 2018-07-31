import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseServerError
from django.test import RequestFactory

from ej_conversations import create_conversation
from ej_conversations.models import Conversation, Comment, FavoriteConversation
from ej_conversations.models.comment import votes_counter
from ej_conversations.routes import conversations, comments
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
    def test_get_all_promoted_conversations(self, get_request, user, conversation, db):
        response = conversations.conversation_list(get_request)
        assert response.get('conversations')._obj.model is Conversation
        assert response.get('can_add_conversation') is False
        assert response.get('owner') is None
        assert response.get('create_link') is None

    def test_conversation_detail_without_being_author(self, get_request, user, conversation, db):
        response = conversations.detail(get_request, conversation)
        assert isinstance(response.get('conversation'), Conversation)
        assert response.get('comment') is None
        assert response.get('owner') is None
        assert response.get('edit_perm') is False
        assert response.get('can_comment') is False
        assert response.get('remaining_comments') == 0
        assert str(response.get('login_link')) is not None

    def test_conversation_detail_being_author(self, get_request_with_user, user, conversation, db):
        ctx = conversations.detail(get_request_with_user, conversation, user)
        assert isinstance(ctx.get('conversation'), Conversation)
        assert ctx['comment'] is None
        assert ctx['owner'] is user
        assert ctx['edit_perm'] is True
        assert ctx['can_comment'] is True
        assert ctx['remaining_comments'] == 2
        assert str(ctx.get('login_link')) is not None

    def test_vote_in_comment(self, request_factory, conversation, comment, db):
        request = request_factory.post('', {'action': 'vote', 'vote': 'agree'})
        user = User.objects.create_user('user@server.com', 'password')
        request.user = user
        conversation.comment = comment
        conversation.save()
        response = conversations.detail(request, conversation)
        assert votes_counter(response.get('comment')) == 1

    def test_invalid_vote_in_comment(self, request_factory, conversation, comment, db):
        request = request_factory.post('', {'action': 'vote', 'vote': 'not agree'})
        user = User.objects.create_user('user@server.com', 'password')
        request.user = user
        conversation.comment = comment
        conversation.save()
        assert isinstance(conversations.detail(request, conversation), HttpResponseServerError)

    def test_user_can_comment(self, request_factory, conversation):
        request = request_factory.post('', {'action': 'comment', 'comment': 'test comment'})
        user = User.objects.create_user('user@server.com', 'password')
        request.user = user
        conversations.detail(request, conversation)
        assert Comment.objects.filter(author=user)[0].content == 'test comment'

    def test_annonymous_user_cannot_comment(self, request_factory, conversation):
        request = request_factory.post('', {'action': 'comment', 'comment': 'test comment'})
        request.user = AnonymousUser()
        response = conversations.detail(request, conversation)
        assert response.get('comment_error') is not None

    def test_user_can_add_conversation_as_favorite(self, request_factory, user, conversation):
        request = request_factory.post('', {'action': 'favorite'})
        request.user = user
        conversations.detail(request, conversation)
        assert FavoriteConversation.objects.filter(user=user, conversation=conversation).exists()

    def test_get_conversation_info(self, get_request_with_user, conversation):
        response = conversations.info(conversation)
        assert response.get('info') is not None

    def test_get_conversation_leaderboard(self, get_request_with_user, conversation):
        response = conversations.leaderboard(conversation)
        assert response.get('info') is not None


class TestConversationComments:
    def test_user_can_get_all_his_comments(self, get_request_with_user, conversation, comment):
        response = comments.comment_list(get_request_with_user, conversation)
        assert len(response.get('approved')) == 1
        assert len(response.get('rejected')) == 0
        assert len(response.get('pending')) == 0
        assert response.get('can_comment') is True
        assert response.get('can_edit') is True

    def test_user_can_get_detail_of_a_comment(self, get_request_with_user, conversation, comment):
        response = comments.comment_detail(conversation, comment)
        assert response.get('comment') is comment
