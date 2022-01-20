from ej_conversations.models import conversation
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_tools.views import *
from ej_tools.tools import BotsWebchatTool, BotsWhatsappTool, MauticTool
from django.core.exceptions import PermissionDenied
from django.test import Client
import pytest


class TestRoutes(ConversationRecipes):
    def test_list_tools(self, conversation_db):
        """
        conversation_db: Sample object from Conversation model;
        rf: pytest-django fixture to send requests on específic routes;
        """
        client = Client()
        client.force_login(conversation_db.author)

        tools_url = conversation_db.patch_url("conversation-tools:index")
        response = client.get(tools_url)

        assert response.context["tools"] != None

    def test_403_for_whatsapp_tool(self, conversation_db, rf):
        tools_url = conversation_db.patch_url("conversation-tools:whatsapp")
        request = rf.get(tools_url)
        request.user = conversation_db.author
        with pytest.raises(PermissionDenied):
            whatsapp(
                request,
                board_slug=conversation_db.board.slug,
                conversation_id=conversation_db.id,
                slug=conversation_db.slug,
            )

    def test_403_for_mautic_tool(self, conversation_db, rf):
        tools_url = conversation_db.patch_url("conversation-tools:mautic")
        request = rf.get(tools_url)
        request.user = conversation_db.author
        with pytest.raises(PermissionDenied):
            mautic(
                request,
                board_slug=conversation_db.board.slug,
                conversation_id=conversation_db.id,
                slug=conversation_db.slug,
            )

    def test_200_for_mautic_tool(self, conversation_db):
        client = Client()
        client.force_login(conversation_db.author)
        conversation_db.author.signature = "listen_to_city"
        conversation_db.author.save()

        tools_url = conversation_db.patch_url("conversation-tools:mautic")
        response = client.get(tools_url, HTTP_HOST="ejlocal")

        assert isinstance(response.context["tool"], MauticTool)

    def test_200_for_whatsapp_tool(self, conversation_db):
        client = Client()
        client.force_login(conversation_db.author)
        conversation_db.author.signature = "listen_to_city"
        conversation_db.author.save()

        tools_url = conversation_db.patch_url("conversation-tools:whatsapp")
        response = client.get(tools_url)

        assert isinstance(response.context["tool"], BotsWhatsappTool)

    def test_200_for_webchat_tool(self, conversation_db):
        client = Client()
        client.force_login(conversation_db.author)
        conversation_db.author.signature = "listen_to_city"
        conversation_db.author.save()

        tools_url = conversation_db.patch_url("conversation-tools:webchat")
        response = client.get(tools_url)

        assert isinstance(response.context["tool"], BotsWebchatTool)

    def test_200_for_webchat_preview_tool(self, conversation_db):
        client = Client()
        client.force_login(conversation_db.author)
        conversation_db.author.signature = "listen_to_city"
        conversation_db.author.save()

        tools_url = conversation_db.patch_url("conversation-tools:webchat-preview")
        response = client.get(tools_url)

        assert response.context["rasa_domain"]
