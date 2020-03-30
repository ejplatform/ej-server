import pytest
from ej_conversations.mommy_recipes import ConversationRecipes
from ej.testing import UrlTester

from ej_conversations.routes_comments import comment_url
from ej_conversations import routes


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
    def test_post_integrations(self, rf, conversation_db, mk_user):
        user = mk_user(email="user@domain.com") 
        request = rf.post('/conversations/' + str(conversation_db.id) + '/' + conversation_db.slug +'/integrations/')
        request.META['HTTP_HOST'] = '0.0.0.0:8000'
        conversation_db.create_comment(user, "comment", status="approved", check_limits=False)
        response = routes.integrations(request, conversation_db, conversation_db.slug)

        assert response.status_code == 200
    
    def test_get_integrations(self, rf, conversation_db, mk_user):
        user = mk_user(email="user@domain.com")
        request = rf.get( '/conversations/' + str(conversation_db.id) + '/' + conversation_db.slug +'/integrations/')
        request.META['HTTP_HOST'] = '0.0.0.0:8000'
        request.user = user
        conversation_db.create_comment(user, "comment", status="approved", check_limits=False)
        response = routes.integrations(request, conversation_db, conversation_db.slug)

        assert response['request'] == request
        assert response['npm_version'] == routes.npm_version()
        assert response['schema'] == 'http'
        assert response['conversation'] == conversation_db
        assert response['menu_links'] == []