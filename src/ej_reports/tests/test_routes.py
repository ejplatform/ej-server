import pytest

from ej_reports.routes import to_pc, df_to_table, map_to_table
from ej_conversations.tests.conftest import api
from ej_conversations.mommy_recipes import *

BASE_URL = '/api/v1'

class TestReportRoutes:
    def test_report_endpoint(self, api, mk_conversation):
        conversation = mk_conversation()
        path = BASE_URL + f'/conversations/{conversation.slug}/reports/'
        print(path)
        data = api.get(path)
        assert data is None
