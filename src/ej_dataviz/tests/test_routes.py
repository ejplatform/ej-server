import pytest
import json
import datetime
from django.urls import reverse
from django.test import RequestFactory
from django.test import Client
from ej_clusters.enums import ClusterStatus
from ej_clusters.models.cluster import Cluster
from ej_clusters.models.stereotype import Stereotype
from ej_clusters.mommy_recipes import ClusterRecipes
from ej_conversations.models.conversation import Conversation

from ej.testing import UrlTester
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_users.models import User
from ej_clusters.models.clusterization import Clusterization
from .examples import general_comments, general_and_cluster_comments, cluster_comments
from ej_dataviz.utils import (
    conversation_has_stereotypes,
    get_cluster_main_comments,
    get_comments_dataframe,
    get_cluster_comments_df,
    filter_comments_by_group,
    get_clusters,
    search_comments_df,
    sort_comments_df,
    OrderByOptions,
)

BASE_URL = "/api/v1"


class TestRoutes(ConversationRecipes, UrlTester):
    admin_urls = [
        "/conversations/1/conversation/report/users/",
        "/conversations/1/conversation/report/comments-report/",
        "/conversations/1/conversation/dashboard/",
    ]

    @pytest.fixture
    def data(self, conversation, board, author_db):
        conversation.author = author_db
        board.owner = author_db
        board.save()
        conversation.board = board
        conversation.save()


class TestReportRoutes(ClusterRecipes):
    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    @pytest.fixture
    def admin_user(self, db):
        admin_user = User.objects.create_superuser("admin@test.com", "pass")
        admin_user.save()
        return admin_user

    @pytest.fixture
    def request_as_admin(self, request_factory, admin_user):
        request = request_factory
        request.user = admin_user
        return request

    @pytest.fixture
    def logged_client(self):
        user = User.objects.get(email="author@domain.com")
        client = Client()
        client.force_login(user)
        return client

    @pytest.fixture()
    def conversation_with_votes(self, conversation, board, author_db):
        user1 = User.objects.create_user("user1@email.br", "password")
        user2 = User.objects.create_user("user2@email.br", "password")
        user3 = User.objects.create_user("user3@email.br", "password")

        conversation.author = author_db
        board.owner = author_db
        board.save()
        conversation.board = board
        conversation.save()

        comment = conversation.create_comment(author_db, "aa", status="approved", check_limits=False)
        comment.vote(user1, "agree")
        comment.vote(user2, "agree")
        comment.vote(user3, "disagree")
        return conversation

    @pytest.fixture
    def conversation_with_comments(self, conversation, board, author_db):
        user1 = User.objects.create_user("user1@email.br", "password")
        user2 = User.objects.create_user("user2@email.br", "password")
        user3 = User.objects.create_user("user3@email.br", "password")

        conversation.author = author_db
        board.owner = author_db
        board.save()
        conversation.board = board
        conversation.save()

        comment = conversation.create_comment(author_db, "aa", status="approved", check_limits=False)
        comment2 = conversation.create_comment(author_db, "aaa", status="approved", check_limits=False)
        comment3 = conversation.create_comment(author_db, "aaaa", status="approved", check_limits=False)
        comment4 = conversation.create_comment(author_db, "test", status="approved", check_limits=False)

        comment.vote(user1, "agree")
        comment.vote(user2, "agree")
        comment.vote(user3, "agree")

        comment2.vote(user1, "agree")
        comment2.vote(user2, "disagree")
        comment2.vote(user3, "disagree")

        comment3.vote(user1, "disagree")
        comment3.vote(user2, "disagree")
        comment3.vote(user3, "disagree")

        comment4.vote(user1, "disagree")
        conversation.save()
        return conversation

    def test_should_get_count_of_votes_in_a_period_of_time(self, conversation_with_votes, logged_client):
        conversation = conversation_with_votes
        today = datetime.datetime.now().date()  # 2022-04-04
        one_week_ago = today - datetime.timedelta(days=7)
        url = reverse("boards:dataviz-votes_over_time", kwargs=conversation.get_url_kwargs())
        url = url + f"?startDate={one_week_ago}&endDate={today}"
        response = logged_client.get(url)
        data = json.loads(response.content)["data"]

        assert response.status_code == 200
        assert len(data) == 8
        assert data[0]["date"] == one_week_ago.strftime("%Y-%m-%dT%H:%M:%SZ")
        assert data[-1]["date"] == today.strftime("%Y-%m-%dT%H:%M:%SZ")

        assert data[0]["value"] == 0
        assert data[1]["value"] == 0
        assert data[2]["value"] == 0
        assert data[3]["value"] == 0
        assert data[4]["value"] == 0
        assert data[5]["value"] == 0
        assert data[6]["value"] == 0
        assert data[7]["value"] == 3

    def test_should_return_error_if_start_date_is_bigger_than_end_date(
        self, conversation, board, author_db, logged_client
    ):
        conversation.author = author_db
        board.owner = author_db
        board.save()
        conversation.board = board
        conversation.save()

        url = reverse("boards:dataviz-votes_over_time", kwargs=conversation.get_url_kwargs())
        url = url + f"?startDate=2021-10-13&endDate=2021-10-06"
        response = logged_client.get(url)
        assert json.loads(response.content) == {"error": "end date must be gratter then start date."}

    def test_missing_params_should_return_error(self, conversation, board, author_db, logged_client):
        conversation.author = author_db
        board.owner = author_db
        board.save()
        conversation.board = board
        conversation.save()

        base_url = reverse("boards:dataviz-votes_over_time", kwargs=conversation.get_url_kwargs())
        response = logged_client.get(base_url)
        assert json.loads(response.content) == {
            "error": "end date and start date should be passed as a parameter."
        }

        url = base_url + f"?startDate=2021-10-06"
        response = logged_client.get(url)
        assert json.loads(response.content) == {
            "error": "end date and start date should be passed as a parameter."
        }

        url = base_url + f"?endDate=2021-10-13"
        response = logged_client.get(url)
        assert json.loads(response.content) == {
            "error": "end date and start date should be passed as a parameter."
        }

    def test_conversation_has_no_stereotypes(self, conversation, board, author_db, logged_client):
        conversation.author = author_db
        board.owner = author_db
        board.save()
        conversation.board = board
        conversation.save()

        clusterization = Clusterization.objects.create(
            conversation=conversation, cluster_status=ClusterStatus.ACTIVE
        )
        Cluster.objects.create(name="name", clusterization=clusterization)

        url = reverse("boards:dataviz-dashboard", kwargs=conversation.get_url_kwargs())
        response = logged_client.get(url)
        assert (
            "Your conversation still does not have defined personas. Without personas, it is not possible to generate opinion groups."
            in response.content.decode()
        )

    def test_conversation_has_stereotypes(self, conversation, board, author_db, logged_client):
        conversation.author = author_db
        board.owner = author_db
        board.save()
        conversation.board = board
        conversation.save()

        clusterization = Clusterization.objects.create(
            conversation=conversation, cluster_status=ClusterStatus.ACTIVE
        )
        cluster = Cluster.objects.create(name="name", clusterization=clusterization)
        stereotype, _ = Stereotype.objects.get_or_create(name="name", owner=author_db)
        cluster.stereotypes.add(stereotype)

        url = reverse("boards:dataviz-dashboard", kwargs=conversation.get_url_kwargs())
        response = logged_client.get(url)
        assert (
            not "Your conversation still does not have defined personas. Without personas, it is not possible to generate opinion groups."
            in response.content.decode()
        )

    def test_get_cluster_main_comments(self, conversation_with_comments):
        clusterization = Clusterization.objects.create(
            conversation=conversation_with_comments, cluster_status=ClusterStatus.ACTIVE
        )
        cluster = Cluster.objects.create(name="name", clusterization=clusterization)
        clusters_main_comments = get_cluster_main_comments(cluster)

        convergence_level = clusters_main_comments["lower_convergence"]["convergence_level"]
        greater_agree = clusters_main_comments["greater_agree"]
        greater_disagree = clusters_main_comments["greater_disagree"]

        assert "lower_convergence" in clusters_main_comments
        assert "greater_agree" in clusters_main_comments
        assert "greater_disagree" in clusters_main_comments
        assert "id" in clusters_main_comments
        assert "cluster_name" in clusters_main_comments

        assert round(convergence_level, 1) == 33.3

        assert round(greater_agree["agree_level"], 1) == 100.0
        assert round(greater_agree["disagree_level"], 1) == 0.0

        assert round(greater_disagree["agree_level"], 1) == 0.0
        assert round(greater_disagree["disagree_level"], 1) == 100.0

    def test_get_comments_dataframe(self, conversation_with_comments):
        comments_df = get_comments_dataframe(conversation_with_comments.comments, "")
        assert comments_df.iloc[[0]].get("group").item() == ""
        assert comments_df.iloc[[1]].get("group").item() == ""
        assert comments_df.iloc[[2]].get("group").item() == ""
        assert comments_df.iloc[[3]].get("group").item() == ""
        assert len(comments_df.index) == 4

    def test_get_cluster_comments_dataframe(self, conversation_with_comments):
        clusterization = Clusterization.objects.create(
            conversation=conversation_with_comments, cluster_status=ClusterStatus.ACTIVE
        )
        cluster = Cluster.objects.create(name="name", clusterization=clusterization)

        comments_df = get_cluster_comments_df(cluster, cluster.name)

        assert comments_df.iloc[[0]].get("group").item() == cluster.name
        assert comments_df.iloc[[1]].get("group").item() == cluster.name
        assert comments_df.iloc[[2]].get("group").item() == cluster.name
        assert comments_df.iloc[[3]].get("group").item() == cluster.name
        assert len(comments_df.index) == 4

    def test_filter_comments_by_group(self, conversation_with_comments):
        clusterization = Clusterization.objects.create(
            conversation=conversation_with_comments, cluster_status=ClusterStatus.ACTIVE
        )
        cluster = Cluster.objects.create(name="name", clusterization=clusterization)

        comments_df = get_comments_dataframe(conversation_with_comments.comments, "")
        clusters = get_clusters(conversation_with_comments)

        filtered_comments_df = filter_comments_by_group(comments_df, clusters, [])
        assert len(filtered_comments_df.index) == 0

        filtered_comments_df = filter_comments_by_group(comments_df, clusters, ["general"])
        assert filtered_comments_df.iloc[[0]].get("group").item() == ""
        assert filtered_comments_df.iloc[[1]].get("group").item() == ""
        assert filtered_comments_df.iloc[[2]].get("group").item() == ""
        assert filtered_comments_df.iloc[[3]].get("group").item() == ""
        assert len(filtered_comments_df.index) == 4

        filtered_comments_df = filter_comments_by_group(comments_df, clusters, [cluster.name])
        assert filtered_comments_df.iloc[[0]].get("group").item() == cluster.name
        assert filtered_comments_df.iloc[[1]].get("group").item() == cluster.name
        assert filtered_comments_df.iloc[[2]].get("group").item() == cluster.name
        assert filtered_comments_df.iloc[[3]].get("group").item() == cluster.name
        assert len(filtered_comments_df.index) == 4

        filtered_comments_df = filter_comments_by_group(comments_df, clusters, ["general", cluster.name])
        assert filtered_comments_df.iloc[[0]].get("group").item() == ""
        assert filtered_comments_df.iloc[[1]].get("group").item() == ""
        assert filtered_comments_df.iloc[[2]].get("group").item() == ""
        assert filtered_comments_df.iloc[[3]].get("group").item() == ""
        assert filtered_comments_df.iloc[[4]].get("group").item() == cluster.name
        assert filtered_comments_df.iloc[[5]].get("group").item() == cluster.name
        assert filtered_comments_df.iloc[[6]].get("group").item() == cluster.name
        assert filtered_comments_df.iloc[[7]].get("group").item() == cluster.name
        assert len(filtered_comments_df.index) == 8

    def test_sort_comments_dataframe(self, conversation_with_comments):
        comments_df = get_comments_dataframe(conversation_with_comments.comments, "")

        sorted_comments_df = sort_comments_df(comments_df, sort_by=OrderByOptions.AGREEMENT)
        assert sorted_comments_df.iloc[[0]].get("content").item() == "aa"
        assert round(sorted_comments_df.iloc[[0]].get("agree").item(), 1) == 100.0
        assert sorted_comments_df.iloc[[1]].get("content").item() == "aaa"
        assert round(sorted_comments_df.iloc[[1]].get("agree").item(), 1) == 33.3
        assert sorted_comments_df.iloc[[2]].get("content").item() == "aaaa"
        assert round(sorted_comments_df.iloc[[2]].get("agree").item(), 1) == 0.0
        assert sorted_comments_df.iloc[[3]].get("content").item() == "test"
        assert round(sorted_comments_df.iloc[[3]].get("agree").item(), 1) == 0.0

        sorted_comments_df = sort_comments_df(comments_df, sort_by=OrderByOptions.DISAGREEMENT)
        assert sorted_comments_df.iloc[[0]].get("content").item() == "aaaa"
        assert round(sorted_comments_df.iloc[[0]].get("disagree").item(), 1) == 100.0
        assert sorted_comments_df.iloc[[1]].get("content").item() == "test"
        assert round(sorted_comments_df.iloc[[1]].get("disagree").item(), 1) == 100.0
        assert sorted_comments_df.iloc[[2]].get("content").item() == "aaa"
        assert round(sorted_comments_df.iloc[[2]].get("disagree").item(), 1) == 66.7
        assert sorted_comments_df.iloc[[3]].get("content").item() == "aa"
        assert round(sorted_comments_df.iloc[[3]].get("disagree").item(), 1) == 0.0

        sorted_comments_df = sort_comments_df(
            comments_df, sort_by=OrderByOptions.PARTICIPATION, sort_order="asc"
        )
        assert sorted_comments_df.iloc[[0]].get("content").item() == "test"
        assert round(sorted_comments_df.iloc[[0]].get("participation").item(), 1) == 33.3
        assert sorted_comments_df.iloc[[1]].get("content").item() == "aa"
        assert round(sorted_comments_df.iloc[[1]].get("participation").item(), 1) == 100.0
        assert sorted_comments_df.iloc[[2]].get("content").item() == "aaa"
        assert round(sorted_comments_df.iloc[[2]].get("participation").item(), 1) == 100.0
        assert sorted_comments_df.iloc[[3]].get("content").item() == "aaaa"
        assert round(sorted_comments_df.iloc[[3]].get("participation").item(), 1) == 100.0

        sorted_comments_df = sort_comments_df(
            comments_df, sort_by=OrderByOptions.CONVERGENCE, sort_order="asc"
        )
        assert sorted_comments_df.iloc[[0]].get("content").item() == "aaa"
        assert round(sorted_comments_df.iloc[[0]].get("convergence").item(), 1) == 33.3
        assert sorted_comments_df.iloc[[1]].get("content").item() == "aa"
        assert round(sorted_comments_df.iloc[[1]].get("convergence").item(), 1) == 100.0
        assert sorted_comments_df.iloc[[2]].get("content").item() == "aaaa"
        assert round(sorted_comments_df.iloc[[2]].get("convergence").item(), 1) == 100.0
        assert sorted_comments_df.iloc[[3]].get("content").item() == "test"
        assert round(sorted_comments_df.iloc[[3]].get("convergence").item(), 1) == 100.0

    def test_search_string_comments_dataframe(self, conversation_with_comments):
        comments_df = get_comments_dataframe(conversation_with_comments.comments, "")
        filtered_comments_df = search_comments_df(comments_df, "aa")
        assert len(filtered_comments_df.index) == 3
        filtered_comments_df = search_comments_df(comments_df, "aaa")
        assert len(filtered_comments_df.index) == 2
        filtered_comments_df = search_comments_df(comments_df, "t")
        assert len(filtered_comments_df.index) == 1

    def test_cards_per_page(self, conversation_with_comments, logged_client):
        conv = conversation_with_comments
        base_url = reverse("boards:dataviz-comments_report_pagination", kwargs=conv.get_url_kwargs())
        url = f"{base_url}?cardsPerPage=1"

        response = logged_client.get(url)
        comments = list(response.context["comments"])
        paginator = response.context["paginator"]
        assert comments == [
            {
                "content": "aa",
                "author": "author",
                "agree": 100.0,
                "disagree": 0.0,
                "skipped": 0.0,
                "convergence": 100.0,
                "participation": 100.0,
                "group": "",
                "id": 0,
            }
        ]
        assert paginator.num_pages == 4

        url = f"{base_url}?cardsPerPage=2"
        response = logged_client.get(url)
        comments = list(response.context["comments"])
        paginator = response.context["paginator"]
        assert comments == [
            {
                "content": "aa",
                "author": "author",
                "agree": 100.0,
                "disagree": 0.0,
                "skipped": 0.0,
                "convergence": 100.0,
                "participation": 100.0,
                "group": "",
                "id": 0,
            },
            {
                "content": "aaa",
                "author": "author",
                "agree": 33.33333333333333,
                "disagree": 66.66666666666666,
                "skipped": 0.0,
                "convergence": 33.33333333333333,
                "participation": 100.0,
                "group": "",
                "id": 1,
            },
        ]
        assert paginator.num_pages == 2

    def test_get_general_comments(self, conversation_with_comments, logged_client):
        conv = conversation_with_comments
        base_url = reverse("boards:dataviz-comments_report_pagination", kwargs=conv.get_url_kwargs())
        response = logged_client.get(base_url)
        comments = list(response.context["comments"])
        assert comments == general_comments

        url = f"{base_url}?clusterFilters=general"
        response = logged_client.get(url)
        comments = list(response.context["comments"])
        assert comments == general_comments

    def test_get_general_and_cluster_comments(self, conversation_with_comments, logged_client):
        conv = conversation_with_comments
        clusterization = Clusterization.objects.create(
            conversation=conv, cluster_status=ClusterStatus.ACTIVE
        )
        cluster = Cluster.objects.create(name="name", clusterization=clusterization)

        base_url = reverse("boards:dataviz-comments_report_pagination", kwargs=conv.get_url_kwargs())
        url = f"{base_url}?clusterFilters=general,{cluster.name}&cardsPerPage=12"
        response = logged_client.get(url)
        comments = list(response.context["comments"])
        assert comments == general_and_cluster_comments

    def test_get_cluster_comments(self, conversation_with_comments, logged_client):
        conv = conversation_with_comments
        clusterization = Clusterization.objects.create(
            conversation=conv, cluster_status=ClusterStatus.ACTIVE
        )
        cluster = Cluster.objects.create(name="name", clusterization=clusterization)

        base_url = reverse("boards:dataviz-comments_report_pagination", kwargs=conv.get_url_kwargs())
        url = f"{base_url}?clusterFilters={cluster.name}"
        response = logged_client.get(url)
        comments = list(response.context["comments"])
        assert comments == cluster_comments

    def test_get_page(self, conversation_with_comments, logged_client):
        conv = conversation_with_comments
        base_url = reverse("boards:dataviz-comments_report_pagination", kwargs=conv.get_url_kwargs())
        url = f"{base_url}?cardsPerPage=1&page=1"

        response = logged_client.get(url)
        comments = list(response.context["comments"])
        assert comments == [
            {
                "content": "aa",
                "author": "author",
                "agree": 100.0,
                "disagree": 0.0,
                "skipped": 0.0,
                "convergence": 100.0,
                "participation": 100.0,
                "group": "",
                "id": 0,
            }
        ]

        url = f"{base_url}?cardsPerPage=1&page=4"
        response = logged_client.get(url)
        comments = list(response.context["comments"])
        assert comments == [
            {
                "content": "test",
                "author": "author",
                "agree": 0.0,
                "disagree": 100.0,
                "skipped": 0.0,
                "convergence": 100.0,
                "participation": 33.33333333333333,
                "group": "",
                "id": 3,
            }
        ]

    def test_conversation_has_stereotypes(self, cluster_db, stereotype_vote):
        cluster_db.stereotypes.add(stereotype_vote.author)
        cluster_db.users.add(cluster_db.clusterization.conversation.author)
        cluster_db.save()
        clusterization = Clusterization.objects.filter(conversation=cluster_db.conversation)
        assert conversation_has_stereotypes(clusterization)

    def test_get_dashboard_with_clusters(self, cluster_db, stereotype_vote, comment, vote, logged_client):
        """
        EJ has several recipes for create objects for testing.
        cluster_db creates objects based on ej_clusters/mommy_recipes.py and testing/fixture_class.py.
        calling cluster_db on method signature creates and cluster belonging to a conversation and clusterization.
        """
        cluster_db.stereotypes.add(stereotype_vote.author)
        cluster_db.users.add(cluster_db.clusterization.conversation.author)
        cluster_db.save()
        conversation = cluster_db.conversation
        comment = conversation.create_comment(
            conversation.author, "aa", status="approved", check_limits=False
        )
        comment.vote(conversation.author, "agree")
        comment.save()
        dashboard_url = reverse("boards:dataviz-dashboard", kwargs=conversation.get_url_kwargs())
        response = logged_client.get(dashboard_url)
        assert response.status_code == 200
        assert response.context["biggest_cluster_data"].get("name") == "cluster"
        assert response.context["biggest_cluster_data"].get("content") == comment.content
        assert response.context["biggest_cluster_data"].get("percentage")

    def test_get_dashboard_without_clusters(self, cluster_db, stereotype_vote, logged_client):
        """
        EJ has several recipes for creating objects for testing.
        cluster_db creates objects based on ej_clusters/mommy_recipes.py and testing/fixture_class.py.
        calling cluster_db on method signature creates an cluster belonging to a conversation and clusterization.
        """
        cluster_db.stereotypes.add(stereotype_vote.author)
        cluster_db.users.add(cluster_db.clusterization.conversation.author)
        cluster_db.save()
        conversation = cluster_db.conversation
        dashboard_url = reverse("boards:dataviz-dashboard", kwargs=conversation.get_url_kwargs())
        response = logged_client.get(dashboard_url)
        assert response.status_code == 200
        assert response.context["biggest_cluster_data"] == {}
