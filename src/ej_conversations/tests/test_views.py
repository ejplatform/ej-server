from django.test import Client
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseServerError, Http404
from pytest import raises
import pytest
from ej_boards.models import Board

from ej_conversations import create_conversation, views
from ej_conversations.models import Comment, FavoriteConversation
from ej_conversations.models.conversation import Conversation
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_conversations.utils import votes_counter
from ej_profiles.tests.test_routes import logged_client
from ej_users.models import User


class TestConversationBase:
    @pytest.mark.skip(reason="No revised test")
    def test_vote_in_comment(self, rf, conversation, comment, db):
        user = User.objects.create_user("user@server.com", "password")
        conversation.comment = comment
        conversation.save()
        request = rf.post("", {"action": "vote", "vote": "agree", "comment_id": comment.id})
        request.user = user
        views.detail(request, conversation)
        assert votes_counter(comment) == 1

    @pytest.mark.skip(reason="No revised test")
    def test_invalid_vote_in_comment(self, rf, conversation, comment):
        request = rf.post("", {"action": "vote", "vote": "INVALID", "comment_id": comment.id})
        user = User.objects.create_user("user@server.com", "password")
        conversation = comment
        conversation.save()
        request.user = user
        with raises(Exception):
            views.detail(request, conversation)

    @pytest.mark.skip(reason="No revised test")
    def test_invalid_action_conversation_detail(self, rf, conversation, comment):
        request = rf.post("", {"action": "invalid"})
        user = User.objects.create_user("user@server.com", "password")
        conversation.save()
        request.user = user
        response = views.detail(request, conversation)
        assert isinstance(response, HttpResponseServerError)

    @pytest.mark.skip(reason="No revised test")
    def test_user_can_comment(self, rf, conversation):
        request = rf.post("", {"action": "comment", "content": "test comment"})
        user = User.objects.create_user("user@server.com", "password")
        request.user = user
        views.detail(request, conversation)
        assert Comment.objects.filter(author=user)[0].content == "test comment"

    @pytest.mark.skip(reason="No revised test")
    def test_user_post_invalid_comment(self, rf, conversation):
        request = rf.post("", {"action": "comment", "content": ""})
        user = User.objects.create_user("user@server.com", "password")
        request.user = user
        response = views.detail(request, conversation)
        assert response["conversation"]

    @pytest.mark.skip(reason="No revised test")
    def test_anonymous_user_cannot_comment(self, rf, conversation):
        request = rf.post("", {"action": "comment", "content": "test comment"})
        request.user = AnonymousUser()
        with raises(PermissionError):
            views.detail(request, conversation)

    @pytest.mark.skip(reason="No revised test")
    def test_user_can_add_conversation_as_favorite(self, rf, user, conversation):
        request = rf.post("", {"action": "favorite"})
        request.user = user
        views.detail(request, conversation)
        assert FavoriteConversation.objects.filter(user=user, conversation=conversation).exists()


class TestConversationComments:
    @pytest.mark.skip(reason="No revised test")
    def test_user_can_get_all_his_comments(self, request_with_user, conversation, user, comment):
        ctx = views.comment_list(request_with_user, conversation)
        assert len(ctx["approved"]) == 1
        assert len(ctx["rejected"]) == 0
        assert len(ctx["pending"]) == 0
        assert ctx["can_edit"]
        assert ctx["can_comment"]

    @pytest.mark.skip(reason="No revised test")
    def test_user_can_get_detail_of_a_comment(self, conversation, comment):
        ctx = views.comment_detail(conversation, comment)
        assert ctx["comment"] is comment

    @pytest.mark.skip(reason="No revised test")
    def test_comment_list_not_promoted_convesation(self, request_with_user, conversation, user):
        conversation.is_promoted = False
        with raises(Http404):
            views.comment_list(request_with_user, conversation)

    @pytest.mark.skip(reason="No revised test")
    def test_udetail_of_a_comment_not_promoted(self, conversation, comment):
        conversation.is_promoted = False
        with raises(Http404):
            views.comment_detail(conversation, comment)


class TestAdminViews(ConversationRecipes):
    @pytest.fixture
    def admin_user(self, db):
        admin_user = User.objects.create_superuser("admin@test.com", "pass")
        admin_user.save()
        return admin_user

    @pytest.fixture
    def logged_admin(self, admin_user):
        client = Client()
        client.force_login(admin_user)
        return client

    @pytest.mark.skip(reason="No revised test")
    def test_create_conversation(self, rf, user):
        request = rf.post(
            "", {"title": "whatever", "tags": "tag", "text": "description", "comments_count": 0}
        )
        request.user = user
        response = views.create(request)
        assert response.status_code == 302
        assert response.url == "/conversations/whatever/stereotypes/"

    @pytest.mark.skip(reason="No revised test")
    def test_create_invalid_conversation(self, rf, user):
        request = rf.post("", {"title": "", "tags": "tag", "text": "description", "comments_count": 0})
        request.user = user
        response = views.create(request)
        assert not response["form"].is_valid()

    @pytest.mark.skip(reason="No revised test")
    def test_edit_conversation(self, rf, conversation):
        request = rf.post(
            "", {"title": "whatever", "tags": "tag", "text": "description", "comments_count": 0}
        )
        request.user = conversation.author
        response = views.edit(request, conversation)
        assert response.status_code == 302
        assert response.url == "/conversations/title/moderate/"

    @pytest.mark.skip(reason="No revised test")
    def test_edit_invalid_conversation(self, rf, conversation):
        request = rf.post("", {"title": "", "tags": "tag", "text": "description", "comments_count": 0})
        request.user = conversation.author
        response = views.edit(request, conversation)
        assert not response["form"].is_valid()

    @pytest.mark.skip(reason="No revised test")
    def test_edit_not_promoted_conversation(self, rf, conversation):
        request = rf.post("", {})
        request.user = conversation.author
        conversation.is_promoted = False
        with raises(Http404):
            views.edit(request, conversation)

    @pytest.mark.skip(reason="No revised test")
    def test_get_edit_conversation(self, rf, conversation):
        user = conversation.author
        comment = conversation.create_comment(user, "comment", "pending")
        conversation.create_comment(user, "comment1")
        comment.status = comment.STATUS.pending
        comment.save()
        request = rf.get("", {})
        request.user = user
        conversation.refresh_from_db()
        response = views.edit(request, conversation)
        assert response["comments"][0] == comment
        assert response["conversation"] == conversation

    def test_admin_can_moderate_comments(self, logged_admin):
        user = User.objects.create_user("user1@email.br", "password")
        board = Board.objects.create(slug="board1", owner=user, description="board")
        client = Client()
        client.login(email="user1@email.br", password="password")
        conversation = create_conversation("foo", "conv1", user, board=board)
        comment_to_approve = conversation.create_comment(
            author=user, content="comment to approve", status="pending"
        )
        comment_to_reject = conversation.create_comment(
            author=user, content="comment to reject", status="pending"
        )
        url = f"/{board.slug}/conversations/{conversation.id}/{conversation.slug}/moderate/"
        client.post(url, {"approved": comment_to_approve.id, "rejected": comment_to_reject.id})

        assert (
            conversation.comments.get(id=comment_to_approve.id).status == comment_to_approve.STATUS.approved
        )
        assert (
            conversation.comments.get(id=comment_to_reject.id).status == comment_to_reject.STATUS.rejected
        )

    def test_admin_can_create_comments(self, logged_admin):
        user = User.objects.create_user("user1@email.br", "password")
        board = Board.objects.create(slug="board1", owner=user, description="board")
        client = Client()
        client.login(email="user1@email.br", password="password")
        conversation = create_conversation("foo", "conv1", user, board=board)
        comments = ["Some comment to test", "Some other comment to test"]
        url = f"/{board.slug}/conversations/{conversation.id}/{conversation.slug}/comments/new/"
        client.post(url, {"comment": comments})

        assert Comment.objects.get(content=comments[0], author=user).status == "approved"
        assert Comment.objects.get(content=comments[1], author=user).status == "approved"

    def test_comments_with_less_than_2_chars_arent_created(self, logged_admin):
        user = User.objects.create_user("user1@email.br", "password")
        board = Board.objects.create(slug="board1", owner=user, description="board")
        client = Client()
        client.login(email="user1@email.br", password="password")
        conversation = create_conversation("foo", "conv1", user, board=board)
        comments = ["A", "Some other comment to test"]
        url = f"/{board.slug}/conversations/{conversation.id}/{conversation.slug}/comments/new/"
        client.post(url, {"comment": comments})

        assert Comment.objects.get(content=comments[1], author=user).status == "approved"
        assert Comment.objects.all().count() == 1

    def test_admin_can_delete_comment(self, logged_admin):
        user = User.objects.create_user("user1@email.br", "password")
        board = Board.objects.create(slug="board1", owner=user, description="board")
        client = Client()
        client.login(email="user1@email.br", password="password")
        conversation = create_conversation("foo", "conv1", user, board=board)
        comment = conversation.create_comment(author=user, content="comment to delete", status="approved")
        url = f"/{board.slug}/conversations/{conversation.id}/{conversation.slug}/comments/delete/"
        client.post(url, {"comment_id": comment.id})

        assert Comment.objects.all().count() == 0

    def test_admin_cant_delete_others_users_comments(self, logged_admin):
        user_1 = User.objects.create_user("user1@email.br", "password")
        user_2 = User.objects.create_user("user2@email.br", "password2")
        board = Board.objects.create(slug="board1", owner=user_1, description="board")
        client = Client()
        client.login(email="user1@email.br", password="password")
        conversation = create_conversation("foo", "conv1", user_2, board=board)
        comment = conversation.create_comment(
            author=user_2, content="comment to not delete", status="approved"
        )
        url = f"/{board.slug}/conversations/{conversation.id}/{conversation.slug}/comments/delete/"
        client.post(url, {"comment_id": comment.id})

        assert Comment.objects.all().count() == 1

    def test_admin_can_check_for_repeated_comment(self, logged_admin):
        user = User.objects.create_user("user1@email.br", "password")
        board = Board.objects.create(slug="board1", owner=user, description="board")
        client = Client()
        client.login(email="user1@email.br", password="password")
        conversation = create_conversation("foo", "conv1", user, board=board)
        comment = conversation.create_comment(author=user, content="comment to check", status="approved")
        url = f"/{board.slug}/conversations/{conversation.id}/{conversation.slug}/comments/check/"
        response = client.post(url, {"comment_content": "comment to check"})

        assert response.status_code == 200

    def test_admin_can_check_for_not_repeated_comment(self, logged_admin):
        user = User.objects.create_user("user1@email.br", "password")
        board = Board.objects.create(slug="board1", owner=user, description="board")
        client = Client()
        client.login(email="user1@email.br", password="password")
        conversation = create_conversation("foo", "conv1", user, board=board)
        conversation.create_comment(author=user, content="comment to check", status="approved")
        url = f"/{board.slug}/conversations/{conversation.id}/{conversation.slug}/comments/check/"
        response = client.post(url, {"comment_content": "new and different comment to check"})

        assert response.status_code == 204
