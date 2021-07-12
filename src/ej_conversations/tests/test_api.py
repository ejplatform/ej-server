from ej_conversations.models import Conversation, Comment
from .examples import COMMENT, CONVERSATION, VOTE, VOTES
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from ej_boards.mommy_recipes import BoardRecipes
import pytest

BASE_URL = "/api/v1"


class TestGetPromotedConversations(BoardRecipes):
    def test_promoted_conversations_endpoint(self, mk_conversation, mk_user, api):
        user = mk_user(email="someemail@domain.com")
        unpromoted_conversation = mk_conversation(is_promoted=False, author=user)
        mk_conversation(is_promoted=True, author=user)
        path = BASE_URL + f"/conversations/?is_promoted=true"
        data = api.get(path)
        assert data.get("count") == 1
        unpromoted_conversation.is_promoted = True
        unpromoted_conversation.save()
        path = BASE_URL + f"/conversations/?is_promoted=true"
        data = api.get(path)
        assert data.get("count") == 2


class TestGetRoutes:
    def test_conversations_endpoint(self, conversation, api):
        path = BASE_URL + f"/conversations/{conversation.id}/"
        data = api.get(path, exclude=["created"])
        assert data == CONVERSATION

    def test_comments_endpoint(self, comment, api):
        path = BASE_URL + f"/comments/{comment.id}/"
        data = api.get(path, exclude=["created"])
        assert data == COMMENT

    def test_vote_endpoint(self, vote, api):
        path = BASE_URL + f"/votes/{vote.id}/"
        data = api.get(path)
        data.pop("created")
        assert data == VOTE

    def test_conversation_votes_endpoint_with_anonymous(self, conversation, vote, api):
        path = BASE_URL + f"/conversations/{conversation.id}/votes/"
        api.get(path)
        assert api.response.status_code == 403

    def test_conversation_votes_endpoint(self, conversation, vote, api):
        auth_token = api.post("/rest-auth/registration/", {"email": "email@server.com", "name": "admin"})
        path = BASE_URL + f"/conversations/{conversation.id}/votes/"
        response = api.client.get(path, {}, HTTP_AUTHORIZATION=f"Token {auth_token.get('key')}")
        data = response.data
        assert type(data) == list
        assert data[0].get("id") == VOTES[0].get("id")
        assert data[0].get("content") == VOTES[0].get("content")
        assert data[0].get("author__metadata__mautic_id") == VOTES[0].get("author__metadata__mautic_id")
        assert data[0].get("author__metadata__analytics_id") == VOTES[0].get(
            "author__metadata__analytics_id"
        )
        assert data[0].get("comment_id") == VOTES[0].get("comment_id")


class TestPostRoutes:
    AUTH_ERROR = {"detail": "Authentication credentials were not provided."}
    EXCLUDES = dict(skip=["created", "modified"])

    def test_post_conversation(self, api, user):
        path = BASE_URL + f"/conversations/"
        post_data = dict(title=CONVERSATION["title"], text=CONVERSATION["text"], author=user.id)

        # Non authenticated user
        assert api.post(path, post_data) == self.AUTH_ERROR

        # Authenticated user
        token = Token.objects.create(user=user)
        _api = APIClient()
        _api.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = _api.post(path, post_data, format="json")
        data = response.data
        del data["created"]
        assert data == CONVERSATION

        # Check if endpoint matches...
        conversation = Conversation.objects.first()
        data = api.get(path + f"{conversation.id}/", **self.EXCLUDES)
        assert data == CONVERSATION

    def test_post_comment(self, api, conversation, user):
        conversation_path = BASE_URL + f"/conversations/{conversation.id}/"
        comments_path = BASE_URL + f"/comments/"
        comment_data = dict(COMMENT, status="pending")
        post_data = dict(
            content=comment_data["content"],
            conversation=conversation.id,
        )

        # Non authenticated user
        assert api.post(comments_path, post_data) == self.AUTH_ERROR

        # Authenticated user
        token = Token.objects.create(user=user)
        _api = APIClient()
        _api.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = _api.post(comments_path, post_data, format="json")
        data = response.data
        del data["created"]
        assert data == comment_data

        # Check if endpoint matches...
        comment = Comment.objects.first()
        data = api.get(comments_path + f"{comment.id}/", **self.EXCLUDES)
        assert data == comment_data
