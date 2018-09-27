import numpy as np
import pytest
from django.test import RequestFactory

from ej.testing import UrlTester
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_dataviz.routes import map_to_table
from ej_users.models import User
from ej_reports.tests.examples import MAP_TO_TABLE

BASE_URL = '/api/v1'


class TestRoutes(ConversationRecipes, UrlTester):
    owner_urls = [
        '/conversations/conversation/reports/',
    ]

    @pytest.fixture
    def data(self, conversation, author_db):
        conversation.author = author_db
        conversation.save()


class TestDataVizRoutes(ConversationRecipes):
    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    @pytest.fixture
    def admin_user(self, db):
        admin_user = User.objects.create_superuser('admin@test.com', 'pass')
        admin_user.save()
        yield admin_user
        admin_user.delete()

    @pytest.fixture
    def request_as_admin(self, request_factory, admin_user):
        request = request_factory
        request.user = admin_user
        return request

    # def test_generate_scatter(self, mk_conversation):
    #     conversation = mk_conversation
    #     response = generate_scatter(request_as_admin, conversation)
    #     expected = {
    #         'plot_data': conversation,
    #     }
    #
    #     assert response == expected

    def test_map_to_table(self, mk_conversation):
        statistics = mk_conversation().statistics()
        mapped_votes = map_to_table(statistics['votes'])

        assert np.array_equal(MAP_TO_TABLE, mapped_votes)
