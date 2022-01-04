import pytest
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from ej_conversations.models import Conversation, Comment, Vote
from .examples import COMMENT, CONVERSATION, VOTE, VOTES
from ej_conversations.models.util import vote_count, statistics_for_user, statistics
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_conversations.enums import Choice
from ej_conversations.models.vote import VoteChannels
from ej_boards.models import Board
from ej_users.models import User

BASE_URL = "/api/v1"


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


class TestApiRoutes:
    AUTH_ERROR = {"detail": "Authentication credentials were not provided."}
    EXCLUDES = dict(skip=["created", "modified"])

    @pytest.fixture
    def admin_user(self, db):
        admin_user = User.objects.create_superuser("admin@test.com", "pass")
        admin_user.save()
        return admin_user

    @pytest.fixture
    def other_user(db):
        user = User.objects.create_user("email2@server.com", "password")
        user.save()
        return user

    def test_post_conversation(self, api, user):
        path = BASE_URL + f"/conversations/"
        board = Board.objects.create(slug="board1", title="My Board", owner=user, description="board")
        post_data = dict(
            title=CONVERSATION["title"], text=CONVERSATION["text"], author=user.id, board=board.id
        )

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

    def test_delete_conversation(self, user):
        path = BASE_URL + f"/conversations/"
        board = Board.objects.create(slug="board1", title="My Board", owner=user, description="board")
        post_data = dict(
            title=CONVERSATION["title"], text=CONVERSATION["text"], author=user.id, board=board.id
        )

        # Authenticated user
        token = Token.objects.create(user=user)
        _api = APIClient()
        _api.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        # creates a conversation
        _api.post(path, post_data, format="json")
        conversation = Conversation.objects.first()
        assert conversation

        # delete the conversation
        path = path + f"{conversation.id}/"
        _api.delete(path, HTTP_AUTHORIZATION=f"Token {token.key}")
        conversation = Conversation.objects.first()
        assert not conversation

    def test_update_conversation(self, user):
        path = BASE_URL + f"/conversations/"
        board = Board.objects.create(slug="board1", title="My Board", owner=user, description="board")
        post_data = dict(
            title=CONVERSATION["title"], text=CONVERSATION["text"], author=user.id, board=board.id
        )

        # Authenticated user
        token = Token.objects.create(user=user)
        _api = APIClient()
        _api.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        # creates a conversation
        response = _api.post(path, post_data, format="json")
        data = response.data
        del data["created"]
        assert data == CONVERSATION

        # updates the conversation
        conversation = Conversation.objects.first()
        path = path + f"{conversation.id}/"
        response = _api.put(
            path,
            data={"title": "updated title", "text": "updated text"},
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

        conversation = Conversation.objects.first()
        assert conversation.title == "updated title"
        assert conversation.text == "updated text"

    def test_post_comment(self, api, conversation, user):
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

    def test_delete_comment(self, conversation, user):
        comments_path = BASE_URL + f"/comments/"
        comment_data = dict(COMMENT, status="pending")
        post_data = dict(
            content=comment_data["content"],
            conversation=conversation.id,
        )

        # Authenticated user
        token = Token.objects.create(user=user)
        _api = APIClient()
        _api.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        # Creates a comment
        _api.post(comments_path, post_data, format="json")
        comment = Comment.objects.first()
        assert comment

        # delete the comment
        path = comments_path + f"{comment.id}/"
        _api.delete(path, HTTP_AUTHORIZATION=f"Token {token.key}")
        comment = Comment.objects.first()
        assert not comment

    def test_update_comment(self, conversation, user):
        comments_path = BASE_URL + f"/comments/"
        comment_data = dict(COMMENT, status="pending")
        post_data = dict(
            content=comment_data["content"],
            conversation=conversation.id,
        )

        # Authenticated user
        token = Token.objects.create(user=user)
        _api = APIClient()
        _api.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        # Creates a comment
        response = _api.post(comments_path, post_data, format="json")
        data = response.data
        del data["created"]
        assert data == comment_data

        # Updates the comment
        comment = Comment.objects.first()
        path = comments_path + f"{comment.id}/"
        update_data = {
            "content": "updated content",
            "rejection_reason": "10",
            "rejection_reason_text": "updated rejection text",
            "status": "rejected",
        }
        response = _api.put(
            path,
            data=update_data,
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

        comment = Comment.objects.first()
        assert comment.content == "updated content"
        assert comment.rejection_reason == 10
        assert comment.rejection_reason_text == "updated rejection text"
        assert comment.status == "rejected"

    def test_post_vote(self, api, comment, user):
        path = BASE_URL + f"/votes/"
        post_data = {
            "analytics_utm": {
                "utm_campaign": 1,
                "utm_test": "test",
            },
            "choice": 1,
            "comment": comment.id,
        }

        # Non authenticated user
        assert api.post(path, post_data) == self.AUTH_ERROR

        # Authenticated user
        token = Token.objects.create(user=user)
        _api = APIClient()
        _api.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        _api.post(path, post_data, format="json")

        vote = comment.votes.last()

        assert vote.analytics_utm == {"utm_campaign": 1, "utm_test": "test"}

    def test_post_vote_without_analytics_utm(self, api, comment, user):
        path = BASE_URL + f"/votes/"
        post_data = {
            "choice": 0,
            "comment": comment.id,
        }

        # Authenticated user
        token = Token.objects.create(user=user)
        _api = APIClient()
        _api.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        _api.post(path, post_data, format="json")

        vote = comment.votes.last()
        assert vote.analytics_utm == None

        post_data["analytics_utm"] = {}
        _api.post(path, post_data, format="json")

        vote = comment.votes.last()
        assert vote.analytics_utm == {}

    def test_post_skipped_vote(self, api, comment, user):
        path = BASE_URL + f"/votes/"
        post_data = {
            "analytics_utm": {
                "utm_campaign": 1,
                "utm_test": "test",
            },
            "choice": 0,
            "comment": comment.id,
        }

        # Authenticated user
        token = Token.objects.create(user=user)
        _api = APIClient()
        _api.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        _api.post(path, post_data, format="json")

        post_data = {
            "analytics_utm": {
                "utm_campaign": 2,
            },
            "choice": 1,
            "comment": comment.id,
        }

        vote = comment.votes.last()
        assert vote.analytics_utm == {"utm_campaign": 1, "utm_test": "test"}

        _api.post(path, post_data, format="json")

        vote = comment.votes.last()
        assert vote.analytics_utm == {
            "utm_campaign": 2,
        }

    def test_delete_vote(self, comment, user, admin_user, other_user):
        path = BASE_URL + f"/votes/"
        post_data = {
            "analytics_utm": {
                "utm_campaign": 1,
                "utm_test": "test",
            },
            "choice": 0,
            "comment": comment.id,
        }

        # Authenticated normal user
        token = Token.objects.create(user=user)
        _api = APIClient()
        _api.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        # Creates a vote
        _api.post(path, post_data, format="json")
        vote = Vote.objects.first()
        assert vote

        path = path + f"{vote.id}/"
        response = _api.delete(path, HTTP_AUTHORIZATION=f"Token {token.key}")
        assert response.status_code == 403

        # User try to delete another user vote
        token3 = Token.objects.create(user=other_user)
        _api.credentials(HTTP_AUTHORIZATION="Token " + token3.key)
        response = _api.delete(path, HTTP_AUTHORIZATION=f"Token {token3.key}")
        assert response.status_code == 403

        # Authenticated superuser
        token2 = Token.objects.create(user=admin_user)
        _api.credentials(HTTP_AUTHORIZATION="Token " + token2.key)
        response = _api.delete(path, HTTP_AUTHORIZATION=f"Token {token2.key}")
        assert response.status_code == 204
        vote = Vote.objects.first()
        assert not vote

    def test_update_vote(self, comment, user):
        path = BASE_URL + f"/votes/"
        post_data = {
            "analytics_utm": {
                "utm_campaign": 1,
                "utm_test": "test",
            },
            "choice": 1,
            "comment": comment.id,
        }

        # Authenticated user
        token = Token.objects.create(user=user)
        _api = APIClient()
        _api.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        # Creates a vote
        _api.post(path, post_data, format="json")
        vote = Vote.objects.first()
        assert vote

        # Updates the vote
        path = path + f"{vote.id}/"
        update_data = {"choice": "-1", "analytics_utm": {"utm_test": "updated test"}}
        _api.put(
            path,
            data=update_data,
            format="json",
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

        vote = Vote.objects.first()
        assert vote.analytics_utm == {"utm_test": "updated test"}
        assert vote.choice == Choice.DISAGREE


class TestConversartionStatistics(ConversationRecipes):
    def test_vote_count_of_a_conversation(self, db, mk_conversation, mk_user):
        conversation = mk_conversation()
        vote_count_result = vote_count(conversation)
        assert vote_count_result == 0

        user = mk_user(email="user@domain.com")
        comment = conversation.create_comment(user, "aa", status="approved", check_limits=False)
        comment.vote(user, "agree")
        vote_count_result = vote_count(conversation)
        assert vote_count_result == 1

    def test_vote_count_agree(self, db, mk_conversation, mk_user):
        conversation = mk_conversation()
        user = mk_user(email="user@domain.com")
        vote_count_result = vote_count(conversation, Choice.AGREE)
        assert vote_count_result == 0

        comment = conversation.create_comment(user, "aa", status="approved", check_limits=False)
        comment.vote(user, "agree")
        vote_count_result = vote_count(conversation, Choice.AGREE)
        assert vote_count_result == 1

        other = mk_user(email="other@domain.com")
        comment = conversation.create_comment(user, "ab", status="approved", check_limits=False)
        comment.vote(other, "disagree")
        vote_count_result = vote_count(conversation, Choice.AGREE)
        assert vote_count_result == 1

    def test_vote_count_disagree(self, db, mk_conversation, mk_user):
        conversation = mk_conversation()
        user = mk_user(email="user@domain.com")
        vote_count_result = vote_count(conversation, Choice.DISAGREE)
        assert vote_count_result == 0

        comment = conversation.create_comment(user, "ac", status="approved", check_limits=False)
        comment.vote(user, "disagree")
        vote_count_result = vote_count(conversation, Choice.DISAGREE)
        assert vote_count_result == 1

    def test_vote_count_skip(self, db, mk_conversation, mk_user):
        conversation = mk_conversation()
        user = mk_user(email="user@domain.com")
        vote_count_result = vote_count(conversation, Choice.SKIP)
        assert vote_count_result == 0

        comment = conversation.create_comment(user, "ad", status="approved", check_limits=False)
        comment.vote(user, "skip")
        vote_count_result = vote_count(conversation, Choice.SKIP)
        assert vote_count_result == 1

    def test_statistics_return(self, db, mk_conversation):
        conversation = mk_conversation()
        statistics_result = statistics(conversation)

        assert "votes" in statistics_result
        assert "agree" in statistics_result["votes"]
        assert "disagree" in statistics_result["votes"]
        assert "skip" in statistics_result["votes"]
        assert "total" in statistics_result["votes"]

        assert "comments" in statistics_result
        assert "approved" in statistics_result["comments"]
        assert "rejected" in statistics_result["comments"]
        assert "pending" in statistics_result["comments"]
        assert "total" in statistics_result["comments"]

        assert "participants" in statistics_result
        assert "voters" in statistics_result["participants"]
        assert "commenters" in statistics_result["participants"]

        assert "channel_votes" in statistics_result
        assert "webchat" in statistics_result["channel_votes"]
        assert "telegram" in statistics_result["channel_votes"]
        assert "whatsapp" in statistics_result["channel_votes"]
        assert "opinion_component" in statistics_result["channel_votes"]
        assert "unknown" in statistics_result["channel_votes"]

        assert "channel_participants" in statistics_result
        assert "webchat" in statistics_result["channel_participants"]
        assert "telegram" in statistics_result["channel_participants"]
        assert "whatsapp" in statistics_result["channel_participants"]
        assert "opinion_component" in statistics_result["channel_participants"]
        assert "unknown" in statistics_result["channel_participants"]

        assert conversation._cached_statistics == statistics_result

    def test_statistics_for_user(self, db, mk_conversation, mk_user):
        conversation = mk_conversation()
        user = mk_user(email="user@domain.com")
        statistics_for_user_result = statistics_for_user(conversation, user)

        assert "votes" in statistics_for_user_result
        assert "missing_votes" in statistics_for_user_result
        assert "participation_ratio" in statistics_for_user_result
        assert "total_comments" in statistics_for_user_result
        assert "comments" in statistics_for_user_result

    def test_statistics_for_channel_votes(self, db, mk_conversation, mk_user):
        conversation = mk_conversation()
        user1 = mk_user(email="user1@domain.com")
        user2 = mk_user(email="user2@domain.com")
        user3 = mk_user(email="user3@domain.com")
        comment = conversation.create_comment(user1, "ad", status="approved", check_limits=False)
        comment2 = conversation.create_comment(user1, "ad2", status="approved", check_limits=False)

        vote = comment.vote(user1, Choice.AGREE)
        vote.channel = VoteChannels.TELEGRAM
        vote.save()

        vote = comment.vote(user2, Choice.AGREE)
        vote.channel = VoteChannels.WHATSAPP
        vote.save()

        vote = comment.vote(user3, Choice.AGREE)
        vote.channel = VoteChannels.WHATSAPP
        vote.save()

        vote = comment2.vote(user1, Choice.AGREE)
        vote.channel = VoteChannels.OPINION_COMPONENT
        vote.save()

        vote = comment2.vote(user2, Choice.AGREE)
        vote.channel = VoteChannels.RASA_WEBCHAT
        vote.save()

        vote = comment2.vote(user3, Choice.AGREE)
        vote.channel = VoteChannels.UNKNOWN
        vote.save()

        statistics = conversation.statistics()
        assert statistics["channel_votes"]["telegram"] == 1
        assert statistics["channel_votes"]["whatsapp"] == 2
        assert statistics["channel_votes"]["opinion_component"] == 1
        assert statistics["channel_votes"]["webchat"] == 1
        assert statistics["channel_votes"]["unknown"] == 1

    def test_statistics_for_channel_participants(self, db, mk_conversation, mk_user):
        conversation = mk_conversation()
        user1 = mk_user(email="user1@domain.com")
        user2 = mk_user(email="user2@domain.com")
        user3 = mk_user(email="user3@domain.com")

        comment = conversation.create_comment(user1, "ad", status="approved", check_limits=False)
        comment2 = conversation.create_comment(user1, "ad2", status="approved", check_limits=False)
        comment3 = conversation.create_comment(user2, "ad3", status="approved", check_limits=False)

        # 3 participantes pelo telegram
        vote = comment.vote(user1, Choice.AGREE)
        vote.channel = VoteChannels.TELEGRAM
        vote.save()

        vote = comment.vote(user2, Choice.AGREE)
        vote.channel = VoteChannels.TELEGRAM
        vote.save()

        vote = comment.vote(user3, Choice.AGREE)
        vote.channel = VoteChannels.TELEGRAM
        vote.save()

        vote = comment2.vote(user1, Choice.AGREE)
        vote.channel = VoteChannels.TELEGRAM
        vote.save()

        vote = comment2.vote(user2, Choice.AGREE)
        vote.channel = VoteChannels.OPINION_COMPONENT
        vote.save()

        vote = comment2.vote(user3, Choice.AGREE)
        vote.channel = VoteChannels.UNKNOWN
        vote.save()

        vote = comment3.vote(user1, Choice.AGREE)
        vote.channel = VoteChannels.RASA_WEBCHAT
        vote.save()

        vote = comment3.vote(user2, Choice.AGREE)
        vote.channel = VoteChannels.WHATSAPP
        vote.save()

        vote = comment3.vote(user3, Choice.AGREE)
        vote.channel = VoteChannels.OPINION_COMPONENT
        vote.save()

        statistics = conversation.statistics()
        assert statistics["channel_participants"]["telegram"] == 3
        assert statistics["channel_participants"]["whatsapp"] == 1
        assert statistics["channel_participants"]["opinion_component"] == 2
        assert statistics["channel_participants"]["webchat"] == 1
        assert statistics["channel_participants"]["unknown"] == 1
