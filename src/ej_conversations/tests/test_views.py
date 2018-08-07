import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseServerError

from ej_conversations import create_conversation
from ej_conversations.models import Conversation, Comment, FavoriteConversation
from ej_conversations.models.comment import votes_counter
from ej_conversations.routes import conversations, comments
from ej_users.models import User


@pytest.fixture
def post_request(rf):
    request = rf.post('')
    request.user = AnonymousUser()
    return request


@pytest.fixture
def request_(rf):
    request = rf.get('')
    request.user = AnonymousUser()
    return request


@pytest.fixture
def request_with_user(rf, user):
    request = rf.get('/testboard/')
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
    def test_get_all_promoted_conversations(self, request_):
        ctx = conversations.conversation_list(request_)
        assert ctx['conversations'].model is Conversation
        assert ctx['can_add_conversation'] is False

    def test_conversation_detail_without_being_author(self, request_, conversation, db):
        ctx = conversations.detail(request_, conversation)
        assert isinstance(ctx.get('conversation'), Conversation)
        assert ctx.get('comment') is None
        assert ctx.get('owner') is None
        assert ctx.get('edit_perm') is False
        assert ctx.get('can_comment') is False
        assert ctx.get('remaining_comments') == 0
        assert str(ctx.get('login_link')) is not None

    def test_conversation_detail_being_author(self, request_with_user, user, conversation, db):
        ctx = conversations.detail(request_with_user, conversation, user)
        assert isinstance(ctx.get('conversation'), Conversation)
        assert ctx['comment'] is None
        assert ctx['owner'] is user
        assert ctx['edit_perm'] is True
        assert ctx['can_comment'] is True
        assert ctx['remaining_comments'] == 2
        assert str(ctx.get('login_link')) is not None

    def test_vote_in_comment(self, rf, conversation, comment, db):
        request = rf.post('', {'action': 'vote', 'vote': 'agree'})
        user = User.objects.create_user('user@server.com', 'password')
        request.user = user
        conversation.comment = comment
        conversation.save()
        response = conversations.detail(request, conversation)
        assert votes_counter(response.get('comment')) == 1

    def test_invalid_vote_in_comment(self, rf, conversation, comment, db):
        request = rf.post('', {'action': 'vote', 'vote': 'not agree'})
        user = User.objects.create_user('user@server.com', 'password')
        request.user = user
        conversation.comment = comment
        conversation.save()
        assert isinstance(conversations.detail(request, conversation), HttpResponseServerError)

    def test_user_can_comment(self, rf, conversation):
        request = rf.post('', {'action': 'comment', 'comment': 'test comment'})
        user = User.objects.create_user('user@server.com', 'password')
        request.user = user
        conversations.detail(request, conversation)
        assert Comment.objects.filter(author=user)[0].content == 'test comment'

    def test_annonymous_user_cannot_comment(self, rf, conversation):
        request = rf.post('', {'action': 'comment', 'comment': 'test comment'})
        request.user = AnonymousUser()
        response = conversations.detail(request, conversation)
        assert response.get('comment_error') is not None

    def test_user_can_add_conversation_as_favorite(self, rf, user, conversation):
        request = rf.post('', {'action': 'favorite'})
        request.user = user
        conversations.detail(request, conversation)
        assert FavoriteConversation.objects.filter(user=user, conversation=conversation).exists()

    def test_get_conversation_info(self, conversation):
        ctx = conversations.info(conversation)
        assert ctx.get('info') is not None

    def test_get_conversation_leaderboard(self, conversation):
        response = conversations.leaderboard(conversation)
        assert response.get('info') is not None


class TestConversationComments:
    def test_user_can_get_all_his_comments(self, request_with_user, conversation, user, comment):
        ctx = comments.comment_list(request_with_user, conversation)
        assert len(ctx['approved']) == 1
        assert len(ctx['rejected']) == 0
        assert len(ctx['pending']) == 0
        assert ctx['can_edit']
        assert ctx['can_comment']

    def test_user_can_get_detail_of_a_comment(self, conversation, comment):
        ctx = comments.comment_detail(conversation, comment)
        assert ctx['comment'] is comment
