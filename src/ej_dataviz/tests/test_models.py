import pytest
from ej_dataviz.models import ToolsLinksHelper


class TestToolsLinksHelper:
    def setup_method(self, method):
        self.environments = {
            "local": "http://localhost:8000",
            "dev": "https://ejplatform.pencillabs.com.br",
            "prod": "https://www.ejplatform.org",
        }

    def test_bot_link_local(self):
        bot_link = ToolsLinksHelper.get_bot_link(self.environments["local"])
        assert bot_link == "https://t.me/DudaLocalBot?start="

    def test_bot_link_dev(self):
        bot_link = ToolsLinksHelper.get_bot_link(self.environments["dev"])
        assert bot_link == "https://t.me/DudaEjDevBot?start="

    def test_bot_link_prod(self):
        bot_link = ToolsLinksHelper.get_bot_link(self.environments["prod"])
        assert bot_link == "https://t.me/DudaEjBot?start="
