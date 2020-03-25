import pytest
from requests import get
from ej_conversations.integrations.utils import npm_version, get_npm_tag
from ej_conversations.mommy_recipes import ConversationRecipes


class TestIntegrationsUtils(ConversationRecipes):
    def test_get_npm_version(self, npm=npm_version):
        tag = get_npm_tag()
        assert tag.status_code == 200

        json = tag.json()
        assert npm() == json

    def test_error_npm_version(self, npm=npm_version):
        tag = get_npm_tag(url="https://registry.npmjs.org/-/package/ej-conversations/dist-tags/erro")
        assert tag.status_code == 405
        
        json = {"latest": "request failed"}
        assert npm(get=tag) == json
