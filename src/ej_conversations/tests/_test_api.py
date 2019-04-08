from ej_conversations.models import Conversation, Comment
from .examples import COMMENT, CONVERSATION, VOTE

BASE_URL = "/api/v1"


class TestGetRoutes:
    def test_conversations_endpoint(self, conversation_db, api):
        path = BASE_URL + f"/conversations/{conversation_db.slug}/"
        data = api.get(path, exclude=["created", "modified"])
        assert data == CONVERSATION

        # Random conversations
        url = BASE_URL + "/conversations/random/"
        assert api.get(url, raw=True).status_code == 200

        # Check inner links work
        assert api.get(path + "user_data/") == {
            "missing_votes": 0,
            "participation_ratio": 0.0,
            "votes": 0,
        }
        assert api.get(path + "votes/") == []
        assert api.get(path + "approved_comments/") == []
        assert api.get(path + "random_comment/") == {
            "error": True,
            "message": "No comments available for this user",
        }

    def test_comments_endpoint(self, comment_db, api):
        data = api.get(f"/comments/{comment_db.id}/")
        assert data == COMMENT

    def test_votes_endpoint(self, vote_db, api):
        # Requesting from non-authenticated user
        assert api.get("/votes/") == {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }

        # Now we force authentication
        api.client.force_login(vote_db.author, backend=None)
        assert api.get(f"/votes/{vote_db.id}/") == VOTE


class TestPostRoutes:
    AUTH_ERROR = {"detail": "Authentication credentials were not provided."}
    EXCLUDES = dict(skip=["created", "modified"])

    def test_post_conversation(self, api, mk_user, category_db):
        user = mk_user(email="conversation_author@domain.com", is_staff=True)
        post_data = dict(
            title=CONVERSATION["title"],
            question=CONVERSATION["question"],
            category=f"http://testserver/categories/{category_db.slug}/",
        )

        # Non authenticated user
        assert api.post("/conversations/", post_data) == self.AUTH_ERROR

        # Authenticated user
        api.client.force_login(user)
        data = api.post("/conversations/", post_data, **self.EXCLUDES)
        assert data == CONVERSATION

        # Check if endpoint matches...
        conversation = Conversation.objects.first()
        data = api.get(f"/conversations/{conversation.slug}/", **self.EXCLUDES)
        assert data == CONVERSATION

    def test_post_comment(self, api, conversation_db, mk_user):
        user = mk_user(email="comment_author@domain.com", is_staff=True)
        comment_data = dict(COMMENT, status="PENDING")
        post_data = dict(
            content=comment_data["content"],
            conversation=f"http://testserver/conversations/{conversation_db.slug}/",
        )

        # Non authenticated user
        assert api.post("/comments/", post_data) == self.AUTH_ERROR

        # Authenticated user
        api.client.force_login(user)
        data = api.post("/comments/", post_data, **self.EXCLUDES)
        assert data == comment_data

        # Check if endpoint matches...
        comment = Comment.objects.first()
        data = api.get(f"/comments/{comment.id}/", **self.EXCLUDES)
        assert data == comment_data
