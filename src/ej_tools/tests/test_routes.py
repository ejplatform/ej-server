from ej_conversations.mommy_recipes import ConversationRecipes
from ej_tools.routes import *
from ej_tools.tools import BotsWebchatTool, BotsWhatsappTool, MauticTool
from django.core.exceptions import PermissionDenied
import pytest


class TestRoutes(ConversationRecipes):
    def test_list_tools(self, conversation_db, rf):
        """
        conversation_db: Sample object from Conversation model;
        rf: pytest-django fixture to send requests on específic routes;
        """
        tools_url = conversation_db.url("conversation-tools:index")
        request = rf.get(tools_url)
        request.user = conversation_db.author
        response = index(request, conversation_db.board, conversation_db, None)
        assert response.get("tools") != None

    def test_403_for_whatsapp_tool(self, conversation_db, rf):
        tools_url = conversation_db.url("conversation-tools:whatsapp")
        request = rf.get(tools_url)
        request.user = conversation_db.author
        with pytest.raises(PermissionDenied):
            whatsapp(request, conversation_db.board, conversation_db, None)

    def test_403_for_mautic_tool(self, conversation_db, rf):
        tools_url = conversation_db.url("conversation-tools:mautic")
        request = rf.get(tools_url)
        request.user = conversation_db.author
        with pytest.raises(PermissionDenied):
            mautic(request, conversation_db.board, conversation_db, None)

    def test_200_for_mautic_tool(self, conversation_db, rf):
        tools_url = conversation_db.url("conversation-tools:mautic")
        request = rf.get(tools_url)
        request.META = {"HTTP_HOST": "http://ejlocal"}
        request.user = conversation_db.author
        conversation_db.author.signature = "listen_to_city"
        response = mautic(request, conversation_db.board, conversation_db, None)
        assert isinstance(response.get("tool"), MauticTool)

    def test_200_for_whatsapp_tool(self, conversation_db, rf):
        tools_url = conversation_db.url("conversation-tools:whatsapp")
        request = rf.get(tools_url)
        request.user = conversation_db.author
        conversation_db.author.signature = "listen_to_city"
        response = whatsapp(request, conversation_db.board, conversation_db, None)
        assert isinstance(response.get("tool"), BotsWhatsappTool)

    def test_200_for_webchat_tool(self, conversation_db, rf):
        tools_url = conversation_db.url("conversation-tools:webchat")
        request = rf.get(tools_url)
        request.user = conversation_db.author
        conversation_db.author.signature = "listen_to_city"
        response = webchat(request, conversation_db)
        assert isinstance(response.get("tool"), BotsWebchatTool)

    def test_200_for_webchat_preview_tool(self, conversation_db, rf):
        tools_url = conversation_db.url("conversation-tools:webchat-preview")
        request = rf.get(tools_url)
        request.user = conversation_db.author
        conversation_db.author.signature = "listen_to_city"
        response = webchat_preview(request, conversation_db.board, conversation_db, "")
        assert response.get("rasa_domain")
