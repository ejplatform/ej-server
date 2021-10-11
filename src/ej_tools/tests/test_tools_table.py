import pytest
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_tools.table import Tools


class TestTemplateGenerator(ConversationRecipes):
    @pytest.fixture
    def tools(self, conversation_db):
        conversation = conversation_db
        return Tools(conversation)

    def test_list_tools(self, tools):
        list_of_tools = tools.list()
        assert len(list_of_tools) > 0
        assert type(list_of_tools) is list

    def test_get_tool_mailing(self, tools):
        mailing_tool = tools.get("Mailing campaign")
        assert mailing_tool
        assert mailing_tool["integration"] != ""
        assert mailing_tool["description"] != ""
        assert mailing_tool["link"] != ""

    def test_get_tool_rasa(self, tools):
        rasa_tool = tools.get("Chatbot")
        assert rasa_tool
        assert rasa_tool["integration"] != ""
        assert rasa_tool["description"] != ""
        assert rasa_tool["link"] != ""
        assert rasa_tool["description_chatbots"] != ""
        assert rasa_tool["description_whatsapp"] != ""
        assert rasa_tool["description_telegram"] != ""
        assert rasa_tool["description_webchat"] != ""

    def test_get_tool_conversation_component(self, tools):
        conversation_component_tool = tools.get("Opinion component")
        assert conversation_component_tool
        assert conversation_component_tool["integration"] != ""
        assert conversation_component_tool["description"] != ""
        assert conversation_component_tool["link"] != ""

    def test_get_tool_mautic(self, tools):
        mautic_tool = tools.get("Mautic")
        assert mautic_tool
        assert mautic_tool["integration"] != ""
        assert mautic_tool["description"] != ""
        assert mautic_tool["link"] != ""

    def test_raise_on_invalid_tool(self, tools):
        with pytest.raises(Exception):
            tools.get("xpto")
