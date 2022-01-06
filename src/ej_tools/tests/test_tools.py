from ej_signatures.models import ListenToCity, ListenToCommunity, SignatureFactory
import pytest
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_tools.tools import BotsTool, MailingTool, MauticTool, OpinionComponentTool


class TestTools(ConversationRecipes):
    @pytest.fixture
    def user_with_listen_to_community(self, user_db):
        user = user_db
        return SignatureFactory.get_user_signature(user)

    @pytest.fixture
    def user_with_listen_to_city(self, user_db):
        user = user_db
        user.signature = "listen_to_city"
        return SignatureFactory.get_user_signature(user)

    def test_list_tools(self, conversation_db, user_with_listen_to_community):
        tools = user_with_listen_to_community.get_conversation_tools(conversation_db)
        assert len(tools) > 0
        assert isinstance(tools[0], MailingTool)
        assert isinstance(tools[1], OpinionComponentTool)
        assert isinstance(tools[2], BotsTool)
        assert isinstance(tools[3], MauticTool)

    def test_get_tool_mailing(self, conversation_db, user_with_listen_to_community):
        mailing_tool = user_with_listen_to_community.get_tool("Mailing campaign", conversation_db)
        assert isinstance(mailing_tool, MailingTool)
        assert mailing_tool.name != ""
        assert mailing_tool.description != ""
        assert mailing_tool.link != ""

    def test_get_tool_bot(self, conversation_db, user_with_listen_to_community):
        bots_tool = user_with_listen_to_community.get_tool("Opinion Bots", conversation_db)
        assert isinstance(bots_tool, BotsTool)
        assert bots_tool.name == "Opinion Bots"
        assert (
            bots_tool.description
            != "Integrate this conversation with a web client, called a webchat.Create a chat on your website page."
        )
        assert bots_tool.link != ""
        assert bots_tool.whatsapp.name == "WhatsApp"
        assert bots_tool.telegram.name == "Telegram"
        assert bots_tool.webchat.name == "Webchat"

    def test_get_tool_conversation_component(self, conversation_db, user_with_listen_to_community):
        conversation_component_tool = user_with_listen_to_community.get_tool(
            "Opinion component", conversation_db
        )
        assert isinstance(conversation_component_tool, OpinionComponentTool)
        assert conversation_component_tool
        assert conversation_component_tool.name == "Opinion component"
        assert conversation_component_tool.description != ""
        assert conversation_component_tool.link != ""

    def test_get_tool_mautic(self, conversation_db, user_with_listen_to_community):
        mautic_tool = user_with_listen_to_community.get_tool("Mautic", conversation_db)
        assert isinstance(mautic_tool, MauticTool)
        assert mautic_tool
        assert mautic_tool.name == "Mautic"
        assert mautic_tool.description != ""
        assert mautic_tool.link != ""

    def test_list_tools_on_listen_to_community_signature(
        self, conversation_db, user_with_listen_to_community
    ):
        tools = user_with_listen_to_community.get_conversation_tools(conversation_db)
        isinstance(tools[0], MailingTool)
        isinstance(tools[1], OpinionComponentTool)
        isinstance(tools[2], BotsTool)
        isinstance(tools[3], MauticTool)

    def test_list_tools_on_listen_to_city_signature(self, conversation_db, user_with_listen_to_city):
        tools = user_with_listen_to_city.get_conversation_tools(conversation_db)
        isinstance(tools[0], MailingTool)
        isinstance(tools[1], OpinionComponentTool)
        isinstance(tools[2], BotsTool)
        isinstance(tools[3], MauticTool)

    def test_if_mautic_tool_is_not_active_on_listen_to_community(
        self, conversation_db, user_with_listen_to_community
    ):
        tools = user_with_listen_to_community.get_conversation_tools(conversation_db)
        assert isinstance(user_with_listen_to_community, ListenToCommunity)
        assert not tools[3].is_active

    def test_if_whatsapp_tool_is_not_active_on_listen_to_community(
        self, conversation_db, user_with_listen_to_community
    ):
        tools = user_with_listen_to_community.get_conversation_tools(conversation_db)
        assert isinstance(user_with_listen_to_community, ListenToCommunity)
        assert not tools[2].whatsapp.is_active

    def test_if_mautic_tool_is_active_on_listen_to_city(self, conversation_db, user_with_listen_to_city):
        tools = user_with_listen_to_city.get_conversation_tools(conversation_db)
        assert isinstance(user_with_listen_to_city, ListenToCity)
        assert tools[3].is_active

    def test_if_whatsapp_tool_is_active_on_listen_to_city(self, conversation_db, user_with_listen_to_city):
        tools = user_with_listen_to_city.get_conversation_tools(conversation_db)
        assert isinstance(user_with_listen_to_city, ListenToCity)
        assert tools[2].whatsapp.is_active
