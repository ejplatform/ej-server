import pytest
import mock
import json
from ej_analysis.airflow_client import AirflowClient
from ej_analysis.visualizations.opinion_component.lib.analytics_wrapper import AnalyticsWrapper
from ej_analysis.visualizations.opinion_component.lib.mongodb_wrapper import MongodbWrapper
from ej_analysis.models import OpinionComponent
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_analysis.routes import *


class MockedAnalyticsWrapper:
    def __init__(self, start_date, end_date, view_id, utm_medium, utm_campaign, utm_source):
        self.start_date = start_date
        self.end_date = end_date
        self.view_id = view_id
        self.utm_medium = utm_medium
        self.utm_campaign = utm_campaign
        self.utm_source = utm_source

    def get_page_engajement(self):
        return 10


class MockedAirflowClient1(AirflowClient):
    def lattest_dag_is_running(self):
        return False

    def trigger_dag(self):
        return True


class MockedMongodbWrapper1:
    def __init__(
        self,
        conversation_id,
        start_date=None,
        end_date=None,
        utm_medium=False,
        utm_campaign=False,
        utm_source=False,
    ):
        pass

    def conversation_data_exists(self):
        return True

    def try_mongodb_connection(self):
        return True

    def get_utm_sources(self):
        return []

    def get_utm_campaigns(self):
        return []

    def get_utm_medium(self):
        return []

    def get_page_aquisition(self):
        return 5


class MockedMongodbWrapper2(MockedMongodbWrapper1):
    def conversation_data_exists(self):
        return False


class TestRoutes(ConversationRecipes):
    @mock.patch("ej_analysis.routes.AirflowClient", mock.Mock())
    @mock.patch("ej_analysis.routes.MongodbWrapper", mock.Mock())
    def test_collecting_data_state(self, conversation_db):
        OpinionComponent.objects.create(conversation_id=conversation_db.id, analytics_property_id=123456)
        assert index({}, conversation_db, conversation_db.slug) == collecting_data_state(conversation_db)

    @mock.patch("ej_analysis.routes.AirflowClient", MockedAirflowClient1)
    @mock.patch("ej_analysis.routes.MongodbWrapper", MockedMongodbWrapper1)
    def test_data_collected_state(self, conversation_db):
        OpinionComponent.objects.create(conversation_id=conversation_db.id, analytics_property_id=123456)
        assert index({}, conversation_db, conversation_db.slug) == {
            "conversation": conversation_db,
            "utm_source_options": [],
            "utm_campaign_options": [],
            "utm_medium_options": [],
            "data_exists": True,
            "mongodb_timeout": False,
            "collecting_is_running": False,
        }

    @mock.patch("ej_analysis.routes.AirflowClient", MockedAirflowClient1)
    @mock.patch("ej_analysis.routes.MongodbWrapper", MockedMongodbWrapper2)
    def test_missing_data_state(self, conversation_db):
        OpinionComponent.objects.create(conversation_id=conversation_db.id, analytics_property_id=123456)
        assert index({}, conversation_db, conversation_db.slug) == missing_data_state(conversation_db)

    @mock.patch("ej_analysis.routes.AnalyticsWrapper", MockedAnalyticsWrapper)
    @mock.patch("ej_analysis.routes.MongodbWrapper", MockedMongodbWrapper1)
    def test_opinion_component_route(self, conversation_db, rf):
        OpinionComponent.objects.create(conversation_id=conversation_db.id, analytics_property_id=123456)
        request = rf.get(
            f"/{conversation_db.id}/{conversation_db.slug}/analysis/opinion_component?startDate=2021-07-01&endDate=2021-07-07&utmMedium=None&utmCampaign=None&utmSource=None"
        )
        response = opinion_component(request, conversation_db, conversation_db.slug)
        assert json.loads(response.content) == {
            "name": "engagement",
            "value": 10,
            "label": "Engagement",
            "children": [{"name": "aquisition", "label": "Aquisition", "value": 5, "children": []}],
        }

    @mock.patch("ej_analysis.routes.AirflowClient", MockedAirflowClient1)
    def test_start_opinion_component_analysis(self, conversation_db, rf):
        OpinionComponent.objects.create(conversation_id=conversation_db.id, analytics_property_id=123456)
        request = rf.post(
            f"/{conversation_db.id}/{conversation_db.slug}/analysis/start_opinion_component_analysis",
            {"conversation_id": conversation_db.id, "analytics_property_id": 123456},
        )
        response = start_opinion_component_analysis(request, conversation_db, conversation_db.slug)
        assert response.status_code == 302
