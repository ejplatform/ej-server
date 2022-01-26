from ej_clusters.enums import ClusterStatus
from ej_clusters.models.cluster import Cluster
from ej_clusters.models.stereotype import Stereotype
import pytest
import json
import datetime
from django.test import RequestFactory
from django.test import Client

from ej.testing import UrlTester
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_users.models import User
from ej_clusters.models.clusterization import Clusterization

BASE_URL = "/api/v1"


class TestRoutes(ConversationRecipes, UrlTester):
    user_urls = ["/conversations/1/conversation/scatter/", "/conversations/1/conversation/word-cloud/"]
    admin_urls = [
        "/conversations/1/conversation/reports/users/",
        "/conversations/1/conversation/reports/comments-report/",
        "/conversations/1/conversation/reports/general-report/",
    ]

    @pytest.fixture
    def data(self, conversation, board, author_db):
        conversation.author = author_db
        board.owner = author_db
        board.save()
        conversation.board = board
        conversation.save()


class TestReportRoutes(ConversationRecipes):
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
    def logged_client(self, author_db):
        user = author_db
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

    def test_report_csv_route(self, request_as_admin, mk_conversation):
        # conversation = mk_conversation()
        # path = BASE_URL + f'/conversations/{conversation.slug}/reports/'
        # request = request_as_admin
        # request.GET = QueryDict('action=generate_csv')
        # request.get(path)
        # response = index(request, conversation)

        # assert response.status_code == 200

        # content = response.content.decode('utf-8')
        # csv.reader(io.StringIO(content))
        # assert CSV_OUT['votes_header'] in content
        # assert CSV_OUT['votes_content'] in content
        # assert CSV_OUT['comments_header'] in content
        # assert CSV_OUT['comments_content'] in content
        # assert CSV_OUT['advanced_comments_header'] in content
        # assert CSV_OUT['advanced_participants_header'] in content
        pass

    def test_should_get_count_of_votes_in_a_period_of_time(self, conversation_with_votes, logged_client):
        conversation = conversation_with_votes
        today = datetime.date.today()
        one_week_ago = today - datetime.timedelta(days=7)
        url = f"/{conversation.board.slug}/conversations/{conversation.id}/{conversation.slug}/reports/votes-over-time/?startDate={one_week_ago}&endDate={today}"
        response = logged_client.get(url)
        data = json.loads(response.content)["data"]

        assert response.status_code == 200
        assert len(data) == 8
        assert data[0]["date"] == one_week_ago.strftime("%Y-%m-%d")
        assert data[-1]["date"] == today.strftime("%Y-%m-%d")

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

        url = f"/{conversation.board.slug}/conversations/{conversation.id}/{conversation.slug}/reports/votes-over-time/?startDate=2021-10-13&endDate=2021-10-06"
        response = logged_client.get(url)
        assert json.loads(response.content) == {"error": "end date must be gratter then start date."}

    def test_missing_params_should_return_error(self, conversation, board, author_db, logged_client):
        conversation.author = author_db
        board.owner = author_db
        board.save()
        conversation.board = board
        conversation.save()

        url = f"/{conversation.board.slug}/conversations/{conversation.id}/{conversation.slug}/reports/votes-over-time/"
        response = logged_client.get(url)
        assert json.loads(response.content) == {
            "error": "end date and start date should be passed as a parameter."
        }

        url = f"/{conversation.board.slug}/conversations/{conversation.id}/{conversation.slug}/reports/votes-over-time/?startDate=2021-10-06"
        response = logged_client.get(url)
        assert json.loads(response.content) == {
            "error": "end date and start date should be passed as a parameter."
        }

        url = f"/{conversation.board.slug}/conversations/{conversation.id}/{conversation.slug}/reports/votes-over-time/?endDate=2021-10-13"
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

        url = f"/{conversation.board.slug}/conversations/{conversation.id}/{conversation.slug}/reports/general-report/"
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

        url = f"/{conversation.board.slug}/conversations/{conversation.id}/{conversation.slug}/reports/general-report/"
        response = logged_client.get(url)
        assert (
            not "Your conversation still does not have defined personas. Without personas, it is not possible to generate opinion groups."
            in response.content.decode()
        )
