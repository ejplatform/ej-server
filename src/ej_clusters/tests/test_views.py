import pytest
from django.utils.translation import gettext_lazy as _
from boogie.testing.pytest import UrlTester
from ej_clusters.enums import ClusterStatus
from ej_clusters.models.cluster import Cluster
from ej_clusters.models.stereotype import Stereotype
from ej_clusters.mommy_recipes import ClusterRecipes
from ej_clusters.models.stereotype_vote import StereotypeVote
from ej_clusters.models.clusterization import Clusterization
from ej_conversations.enums import Choice
from ej_conversations.models.comment import Comment
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_clusters.views import (
    stereotype_votes,
    stereotype_votes_create,
)
from ej_clusters.stereotypes_utils import extract_choice_id, order_stereotype_votes_by


class TestRoutes(ConversationRecipes, UrlTester):
    user_urls = ["/stereotypes/"]
    owner_urls = ["/conversations/1/conversation/stereotypes/"]

    @pytest.fixture
    def data(self, conversation, board, author_db):
        conversation.author = author_db
        board.owner = author_db
        board.save()
        conversation.board = board
        conversation.save()


class TestStereotypeVoteRoute(ClusterRecipes):
    @pytest.fixture
    def conversation_with_board(self, conversation, board, user_db):
        conversation.author = user_db
        board.owner = user_db
        board.save()
        conversation.board = board
        conversation.save()
        return conversation

    def test_get_stereotype_vote_page_without_stereotypes(self, conversation_with_board, user_db, rf):
        request = rf.get("", {})
        request.user = user_db
        Clusterization.objects.create(
            conversation=conversation_with_board, cluster_status=ClusterStatus.ACTIVE
        )

        response = stereotype_votes(request, conversation_id=conversation_with_board.id)
        assert response.status_code == 200

    def test_get_stereotype_vote_page_with_one_stereotype(self, conversation_with_board, user_db, rf):
        request = rf.get("", {})
        request.user = user_db
        clusterization = Clusterization.objects.create(
            conversation=conversation_with_board, cluster_status=ClusterStatus.ACTIVE
        )
        cluster = Cluster.objects.create(name="name", clusterization=clusterization)
        stereotype, _ = Stereotype.objects.get_or_create(name="name", owner=user_db)
        cluster.stereotypes.add(stereotype)

        response = stereotype_votes(request, conversation_id=conversation_with_board.id)
        assert response.status_code == 200

    def test_get_stereotype_vote_page_with_stereotypes_selected(self, conversation_with_board, user_db, rf):
        clusterization = Clusterization.objects.create(
            conversation=conversation_with_board, cluster_status=ClusterStatus.ACTIVE
        )

        cluster = Cluster.objects.create(name="name", clusterization=clusterization)
        stereotype, _ = Stereotype.objects.get_or_create(name="name", owner=user_db)
        second_stereotype, _ = Stereotype.objects.get_or_create(name="second stereotype", owner=user_db)
        cluster.stereotypes.add(stereotype)
        cluster.stereotypes.add(second_stereotype)
        request = rf.get("", {"stereotype-select": second_stereotype.id})
        request.user = user_db

        response = stereotype_votes(request, conversation_id=conversation_with_board.id)
        assert response.status_code == 200

    def test_post_update_stereotype_vote_page_with_stereotypes(
        self, conversation_with_board, user_db, board, rf
    ):
        clusterization = Clusterization.objects.create(
            conversation=conversation_with_board, cluster_status=ClusterStatus.ACTIVE
        )
        comment = Comment.objects.create(
            content="comment", conversation=conversation_with_board, author=user_db
        )
        stereotype, _ = Stereotype.objects.get_or_create(name="name", owner=user_db)
        cluster = Cluster.objects.create(name="name", clusterization=clusterization)
        cluster.stereotypes.add(stereotype)
        stereotype_vote = StereotypeVote.objects.create(
            choice=Choice.AGREE, comment=comment, author_id=stereotype.id
        )
        assert stereotype_vote.choice == Choice.AGREE

        request = rf.post(
            f"{conversation_with_board.get_absolute_url()}stereotypes/",
            {"update": f"skip-{stereotype_vote.id}", "stereotype": stereotype.id},
        )
        request.user = user_db
        response = stereotype_votes(request, conversation_id=conversation_with_board.id)
        stereotype_vote.refresh_from_db()
        content = response.content.decode("utf-8")
        assert response.status_code == 200

    def test_post_delete_stereotype_vote_page_with_stereotypes(self, conversation_with_board, user_db, rf):
        clusterization = Clusterization.objects.create(
            conversation=conversation_with_board, cluster_status=ClusterStatus.ACTIVE
        )
        comment = Comment.objects.create(
            content="comment", conversation=conversation_with_board, author=user_db
        )
        stereotype, _ = Stereotype.objects.get_or_create(name="name", owner=user_db)
        cluster = Cluster.objects.create(name="name", clusterization=clusterization)
        cluster.stereotypes.add(stereotype)
        stereotype_vote = StereotypeVote.objects.create(
            choice=Choice.AGREE, comment=comment, author_id=stereotype.id
        )

        request = rf.post(
            f"{conversation_with_board.get_absolute_url()}stereotypes/",
            {"update": f"delete-{stereotype_vote.id}", "stereotype": stereotype.id},
        )
        request.user = user_db
        response = stereotype_votes(request, conversation_id=conversation_with_board.id)

        assert not StereotypeVote.objects.filter(id=stereotype_vote.id).exists()
        assert response.status_code == 200

    def test_auxiliar_extract_choice_id(self):
        response = extract_choice_id("delete-id")
        assert response["id"] == "id"
        assert response["choice"] == "delete"

    def test_auxiliar_order_by_stereotype_vote_choice(self, conversation_with_board, user_db):
        clusterization = Clusterization.objects.create(
            conversation=conversation_with_board, cluster_status=ClusterStatus.ACTIVE
        )
        comment = Comment.objects.create(
            content="comment", conversation=conversation_with_board, author=user_db
        )
        comment2 = Comment.objects.create(
            content="comment 2", conversation=conversation_with_board, author=user_db
        )
        comment3 = Comment.objects.create(
            content="comment 3", conversation=conversation_with_board, author=user_db
        )
        stereotype, _ = Stereotype.objects.get_or_create(name="name", owner=user_db)
        cluster = Cluster.objects.create(name="name", clusterization=clusterization)
        cluster.stereotypes.add(stereotype)
        stereotype_vote_agree = StereotypeVote.objects.create(
            choice=Choice.AGREE, comment=comment, author_id=stereotype.id
        )
        stereotype_vote_skip = StereotypeVote.objects.create(
            choice=Choice.SKIP, comment=comment2, author_id=stereotype.id
        )
        stereotype_vote_disagree = StereotypeVote.objects.create(
            choice=Choice.DISAGREE, comment=comment3, author_id=stereotype.id
        )

        steoreotype_votes_list = clusterization.stereotype_votes.filter(author=stereotype)
        return_with_agree_first = order_stereotype_votes_by(steoreotype_votes_list, 1, "-")
        assert return_with_agree_first.first() == stereotype_vote_agree
        assert return_with_agree_first.last() == stereotype_vote_disagree

        return_with_disagree_first = order_stereotype_votes_by(steoreotype_votes_list, -1, "-")
        assert return_with_disagree_first.first() == stereotype_vote_disagree
        assert return_with_disagree_first.last() == stereotype_vote_agree

        return_with_skip_first = order_stereotype_votes_by(steoreotype_votes_list, 0, "-")
        assert return_with_skip_first.first() == stereotype_vote_skip
        assert return_with_skip_first.last() == stereotype_vote_disagree

    def test_auxiliar_post_create_stereotype_vote(self, conversation_with_board, user_db, rf):
        clusterization = Clusterization.objects.create(
            conversation=conversation_with_board, cluster_status=ClusterStatus.ACTIVE
        )
        comment = Comment.objects.create(
            content="comment", conversation=conversation_with_board, author=user_db
        )
        cluster = Cluster.objects.create(name="name", clusterization=clusterization)
        stereotype, _ = Stereotype.objects.get_or_create(name="name", owner=user_db)
        cluster.stereotypes.add(stereotype)

        request = rf.post(
            f"{conversation_with_board.get_absolute_url()}stereotypes/stereotype-votes/create",
            {"comment": comment.id, "author": stereotype.id, "choice": "1"},
        )
        request.user = user_db
        response = stereotype_votes_create(request, conversation_id=conversation_with_board.id)
        assert response.content.decode() == str(
            clusterization.stereotype_votes.filter(author=stereotype).first().id
        )
