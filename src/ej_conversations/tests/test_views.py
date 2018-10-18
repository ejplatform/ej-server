import pytest
from django.contrib.auth.models import AnonymousUser
from pytest import raises
from django.http import HttpResponseServerError, Http404

from ej_conversations import create_conversation
from ej_conversations.models import Comment, FavoriteConversation
from ej_conversations.models.utils import votes_counter
from ej_conversations.routes import conversations, comments, admin
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
    return create_conversation(text='test', title='title', author=user, is_promoted=True)


@pytest.fixture
def comment(db, conversation, user):
    return conversation.create_comment(user, 'content', 'approved')


class TestConversationBase:
    def test_vote_in_comment(self, rf, conversation, comment, db):
        user = User.objects.create_user('user@server.com', 'password')
        conversation.comment = comment
        conversation.save()
        request = rf.post('', {'action': 'vote', 'vote': 'agree', 'comment_id': comment.id})
        request.user = user
        conversations.detail(request, conversation)
        assert votes_counter(comment) == 1

    def test_invalid_vote_in_comment(self, rf, conversation, comment):
        request = rf.post('', {'action': 'vote', 'vote': 'INVALID', 'comment_id': comment.id})
        user = User.objects.create_user('user@server.com', 'password')
        conversation = comment
        conversation.save()
        request.user = user
        with raises(Exception):
            conversations.detail(request, conversation)

    def test_user_can_comment(self, rf, conversation):
        request = rf.post('', {'action': 'comment', 'content': 'test comment'})
        user = User.objects.create_user('user@server.com', 'password')
        request.user = user
        conversations.detail(request, conversation)
        assert Comment.objects.filter(author=user)[0].content == 'test comment'

    def test_anonymous_user_cannot_comment(self, rf, conversation):
        request = rf.post('', {'action': 'comment', 'content': 'test comment'})
        request.user = AnonymousUser()
        with raises(PermissionError):
            conversations.detail(request, conversation)

    def test_user_can_add_conversation_as_favorite(self, rf, user, conversation):
        request = rf.post('', {'action': 'favorite'})
        request.user = user
        conversations.detail(request, conversation)
        assert FavoriteConversation.objects.filter(user=user, conversation=conversation).exists()


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


class TestAdminViews:
    def test_author_can_moderate_conversation_approving_comment(self, rf, conversation):
        other = User.objects.create_user('email@email.br', 'pass')
        comment = conversation.create_comment(other, 'aa', check_limits=False)
        assert comment.status == comment.STATUS.pending
        request = rf.post('', {'comment': comment.id, 'vote': 'approve'})
        request.user = User.objects.get(email='email@server.com')
        admin.moderate(request, conversation)
        comment.refresh_from_db()
        assert comment.status == comment.STATUS.approved

    def test_author_can_moderate_conversation_rejecting_comment(self, rf, conversation):
        other = User.objects.create_user('email@email.br', 'pass')
        comment = conversation.create_comment(other, 'aa', check_limits=False)
        assert comment.status == comment.STATUS.pending
        request = rf.post('', {'comment': comment.id, 'vote': 'disapprove', 'rejection_reason': 'offensive_language'})
        request.user = User.objects.get(email='email@server.com')
        admin.moderate(request, conversation)
        comment.refresh_from_db()
        assert comment.status == comment.STATUS.rejected

    def test_author_try_moderate_invalid_vote(self, rf, conversation):
        other = User.objects.create_user('email@email.br', 'pass')
        comment = conversation.create_comment(other, 'aa', check_limits=False)
        request = rf.post('', {'comment': comment.id, 'vote': 'other', 'rejection_reason': 'offensive_language'})
        request.user = User.objects.get(email='email@server.com')
        response = admin.moderate(request, conversation)
        assert isinstance(response, HttpResponseServerError)

    def test_author_try_moderate_unpromoted_conversation(self, rf, conversation):
        request = rf.get('')
        request.user = User.objects.get(email='email@server.com')
        conversation.is_promoted = False
        conversation.save()
        with raises(Http404):
            admin.moderate(request, conversation)
