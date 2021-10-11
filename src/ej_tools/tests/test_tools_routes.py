import pytest
from ej_conversations.mommy_recipes import ConversationRecipes
from ej.testing import UrlTester

from ej_conversations.routes_comments import comment_url
from ej_conversations import routes
from ej_tools.models import RasaConversation, ConversationMautic
from ej_users.models import User

TEST_DOMAIN = "https://domain.com.br"
CONVERSATION_BOARD_URL = "/board-slug/conversations"


class TestIntegrationsRoutes(ConversationRecipes):
    def test_get_tools(self, user_client, conversation_db):
        response = user_client.get(
            "/conversations/" + str(conversation_db.id) + "/" + conversation_db.slug + "/tools"
        )
        assert response.status_code == 200

    def test_chatbots(self, user_client, conversation_db):
        response = user_client.get(
            "/conversations/" + str(conversation_db.id) + "/" + conversation_db.slug + "/tools/chatbot"
        )
        assert response.status_code == 200


class TestRemoveRasaConnection(ConversationRecipes):
    def test_superuser_delete_connection(self, conversation_db, admin_client):
        connection = RasaConversation.objects.create(conversation=conversation_db, domain=TEST_DOMAIN)
        connection_id = connection.id
        response = admin_client.get(
            conversation_db.get_absolute_url() + "tools/chatbot/rasa/delete/" + str(connection_id)
        )

        assert response.status_code == 302
        assert not RasaConversation.objects.filter(id=connection_id).exists()

    def test_author_delete_connection(self, conversation_db, user_client):
        user_client.force_login(conversation_db.author)
        connection = RasaConversation.objects.create(conversation=conversation_db, domain=TEST_DOMAIN)
        connection_id = connection.id
        response = user_client.get(
            conversation_db.get_absolute_url() + "tools/chatbot/rasa/delete/" + str(connection_id)
        )

        assert response.status_code == 302
        assert not RasaConversation.objects.filter(id=connection_id).exists()

    def test_try_other_user_delete_connection(self, conversation_db, user_client):
        connection = RasaConversation.objects.create(conversation=conversation_db, domain=TEST_DOMAIN)
        connection_id = connection.id
        response = user_client.get(
            conversation_db.get_absolute_url() + "tools/chatbot/rasa/delete/" + str(connection_id)
        )
        assert response.status_code == 302
        assert RasaConversation.objects.filter(id=connection_id).exists()

    def test_try_unlogged_delete_connection(self, conversation_db, client):
        connection = RasaConversation.objects.create(conversation=conversation_db, domain=TEST_DOMAIN)
        connection_id = connection.id

        response = client.get(
            conversation_db.get_absolute_url() + "tools/chatbot/rasa/delete/" + str(connection_id)
        )
        assert response.status_code == 302
        assert RasaConversation.objects.filter(id=connection_id).exists()


class TestRemoveMauticConnection(ConversationRecipes):
    def test_superuser_delete_mautic_connection(self, conversation_db, admin_client):
        mautic_connection = ConversationMautic.objects.create(conversation=conversation_db, url=TEST_DOMAIN)
        mautic_connection_id = mautic_connection.id
        response = admin_client.get(
            conversation_db.get_absolute_url() + "tools/mautic/delete/" + str(mautic_connection_id)
        )

        assert response.status_code == 302
        assert not ConversationMautic.objects.filter(id=mautic_connection_id).exists()

    def test_author_delete_mautic_connection(self, conversation_db, user_client):
        user_client.force_login(conversation_db.author)
        mautic_connection = ConversationMautic.objects.create(conversation=conversation_db, url=TEST_DOMAIN)
        mautic_connection_id = mautic_connection.id
        response = user_client.get(
            conversation_db.get_absolute_url() + "tools/mautic/delete/" + str(mautic_connection_id)
        )

        assert response.status_code == 302
        assert not ConversationMautic.objects.filter(id=mautic_connection_id).exists()

    def test_try_other_user_delete_mautic_connection(self, conversation_db, user_client):
        mautic_connection = ConversationMautic.objects.create(conversation=conversation_db, url=TEST_DOMAIN)
        mautic_connection_id = mautic_connection.id

        response = user_client.get(
            conversation_db.get_absolute_url() + "tools/mautic/delete/" + str(mautic_connection_id)
        )
        assert response.status_code == 302
        assert (
            response.url
            == f"/login/?next={conversation_db.get_absolute_url() + 'tools/mautic/delete/' + str(mautic_connection_id)}"
        )
        assert ConversationMautic.objects.filter(id=mautic_connection_id).exists()

    def test_try_unlogged_delete_mautic_connection(self, conversation_db, client):
        mautic_connection = ConversationMautic.objects.create(conversation=conversation_db, url=TEST_DOMAIN)
        mautic_connection_id = mautic_connection.id

        response = client.get(
            conversation_db.get_absolute_url() + "tools/mautic/delete/" + str(mautic_connection_id)
        )
        assert (
            response.url
            == f"/login/?next={conversation_db.get_absolute_url() + 'tools/mautic/delete/' + str(mautic_connection_id)}"
        )
        assert ConversationMautic.objects.filter(id=mautic_connection_id).exists()
