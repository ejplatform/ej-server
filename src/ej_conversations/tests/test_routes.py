import pytest
from ej_conversations.mommy_recipes import ConversationRecipes
from ej.testing import UrlTester

from ej_conversations.routes_comments import comment_url
from ej_conversations import routes
from ej_conversations.tools.models import RasaConversation
from ej_users.models import User

TEST_DOMAIN = "https://domain.com.br"

class TestRoutes(UrlTester, ConversationRecipes):
    public_urls = ["/conversations/"]
    user_urls = [
        "/conversations/1/slug/",
        # '/comments/<id>-<hash>/'
    ]
    admin_urls = ["/conversations/add/"]
    owner_urls = ["/conversations/1/slug/edit/", "/conversations/1/slug/moderate/"]

    def get_data(self, request):
        conversation = request.getfixturevalue("conversation")
        conversation.author = request.getfixturevalue("author_db")
        conversation.is_promoted = True
        conversation.save()

    def test_can_view_user_url(self, user_client, comment_db):
        url = comment_url(comment_db)
        response = user_client.get(url)
        assert response.status_code == 200


class TestIntegrationsRoutes(ConversationRecipes):
    def test_get_tools(self, user_client, conversation_db, mk_user):
        response = user_client.get('/conversations/' + str(conversation_db.id)
                                   + '/' + conversation_db.slug + '/tools')
        assert response.status_code == 200


class TestRemoveRasaConnection(ConversationRecipes):
    def test_superuser_delete_connection(self, conversation_db, admin_client):
        connection = RasaConversation.objects.create(conversation=conversation_db, domain=TEST_DOMAIN)
        connection_id = connection.id
        response = admin_client.get('/conversations/' + str(conversation_db.id)
                                   + '/' + conversation_db.slug + '/tools/rasa/delete/' + str(connection_id))
        

        assert response.status_code == 302
        assert not RasaConversation.objects.filter(id=connection_id).exists()
    
    def test_author_delete_connection(self, conversation_db, user_client):
        user_client.force_login(conversation_db.author)
        connection = RasaConversation.objects.create(conversation=conversation_db, domain=TEST_DOMAIN)
        connection_id = connection.id
        response = user_client.get('/conversations/' + str(conversation_db.id)
                                   + '/' + conversation_db.slug + '/tools/rasa/delete/' + str(connection_id))

        assert response.status_code == 302
        assert not RasaConversation.objects.filter(id=connection_id).exists()

    def test_try_other_user_delete_connection(self, conversation_db, user_client):
        connection = RasaConversation.objects.create(conversation=conversation_db, domain=TEST_DOMAIN)
        connection_id = connection.id

        with pytest.raises(PermissionError):
            response = user_client.get('/conversations/' + str(conversation_db.id)
                                   + '/' + conversation_db.slug + '/tools/rasa/delete/' + str(connection_id)) 
            assert RasaConversation.objects.filter(id=connection_id).exists()
    
    def test_try_unlogged_delete_connection(self, conversation_db, client):
        connection = RasaConversation.objects.create(conversation=conversation_db, domain=TEST_DOMAIN)
        connection_id = connection.id

        with pytest.raises(PermissionError):
            response = client.get('/conversations/' + str(conversation_db.id)
                                   + '/' + conversation_db.slug + '/tools/rasa/delete/' + str(connection_id)) 
            assert RasaConversation.objects.filter(id=connection_id).exists()
