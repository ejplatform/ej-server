import pytest
from django.test import RequestFactory

from ej.testing import UrlTester
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_users.models import User

BASE_URL = "/api/v1"


class TestRoutes(ConversationRecipes, UrlTester):
    user_urls = ["/conversations/1/conversation/scatter/", "/conversations/1/conversation/word-cloud/"]
    admin_urls = ["/conversations/1/conversation/reports/", "/conversations/1/conversation/reports/users/"]

    @pytest.fixture
    def data(self, conversation, author_db):
        conversation.author = author_db
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
