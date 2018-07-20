import pytest
import csv
import io
from django.test import RequestFactory
from django.http import QueryDict

from ej_reports.routes import to_pc, df_to_table, map_to_table, index
from ej_conversations.mommy_recipes import *
from ej_users.models import User, username
from .examples import REPORT_RESPONSE, CSV_OUT
BASE_URL = '/api/v1'


@pytest.fixture
def request_factory():
    return RequestFactory()

@pytest.fixture
def admin_user(db):
    admin_user = User.objects.create_superuser('usr', 'admin@test.com', 'pass')
    admin_user.save()
    yield admin_user
    admin_user.delete()

@pytest.fixture
def request_as_admin(request_factory, admin_user):
    request = request_factory
    request.user = admin_user
    return request

class TestReportRoutes:
    def test_report_route(self, request_as_admin, mk_conversation):
        conversation = mk_conversation()
        path = BASE_URL + f'/conversations/{conversation.slug}/reports/'
        print(path)
        request = request_as_admin
        request.GET = QueryDict('')
        request.get(path)
        response = index(request, conversation)

        assert  REPORT_RESPONSE['statistics'] in response.values()

    def test_report_csv_route(self, request_as_admin, mk_conversation):
        conversation = mk_conversation()
        path = BASE_URL + f'/conversations/{conversation.slug}/reports/'
        print(path)
        request = request_as_admin
        request.GET = QueryDict('action=generate_csv')
        request.get(path)
        response = index(request, conversation)

        assert response.status_code == 200
        content = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        print(content)
        assert CSV_OUT['votes_header'] in content
        assert CSV_OUT['votes_content'] in content
        assert CSV_OUT['comments_header'] in content
        assert CSV_OUT['comments_content'] in content
        assert CSV_OUT['advanced_comments_header'] in content
        assert CSV_OUT['advanced_participants_header'] in content

    def test_df_to_table_func(self):
        pass
