from ej_conversations.models import Conversation, Comment
from .examples import COMMENT, CONVERSATION, VOTE
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
import pytest

BASE_URL = "/api/v1"


class TestGetRoutes:
    def test_conversations_endpoint(self, conversation, api):
        path = BASE_URL + f"/conversations/{conversation.id}/"
        data = api.get(path, exclude=["created"])
        assert data == CONVERSATION

    def test_conversations_reports_endpoint(self, conversation, api):
        path = BASE_URL + f"/conversations/{conversation.id}/reports/?fmt=csv&export=votes"
        _api = APIClient()
        with pytest.raises(TypeError):
            _api.get(path, {})
        response = _api.get(path, {}, HTTP_ACCEPT='text/csv')
        assert response.status_code == 200

    def test_comments_endpoint(self, comment, api):
        path = BASE_URL + f"/comments/{comment.id}/"
        data = api.get(path, exclude=["created"])
        assert data == COMMENT

    def test_votes_endpoint(self, vote, api):
        path = BASE_URL + f"/votes/{vote.id}/"
        data = api.get(path)
        data.pop('created')
        assert data == VOTE


class TestPostRoutes:
    AUTH_ERROR = {"detail": "Authentication credentials were not provided."}
    EXCLUDES = dict(skip=["created", "modified"])

    def test_post_conversation(self, api, user):
        path = BASE_URL + f"/conversations/"
        post_data = dict(
            title=CONVERSATION["title"],
            text=CONVERSATION["text"],
            author=user.id
        )

        # Non authenticated user
        assert api.post(path, post_data) == self.AUTH_ERROR

        # Authenticated user
        token = Token.objects.create(user=user)
        _api = APIClient()
        _api.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = _api.post(path, post_data, format='json')
        data = response.data
        del data['created']
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
        _api.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = _api.post(comments_path, post_data, format='json')
        data = response.data
        del data['created']
        assert data == comment_data

        # Check if endpoint matches...
        comment = Comment.objects.first()
        data = api.get(comments_path + f"{comment.id}/", **self.EXCLUDES)
        assert data == comment_data
