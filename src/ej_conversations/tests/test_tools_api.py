import pytest
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from ej_conversations.tools.models import RasaConversation
from ej_users.models import User

BASE_URL = "/api/v1"
TEST_DOMAIN = "https://domain.com.br"


class TestRemoveRasaConnection:
    def test_superuser_delete_connection(self, conversation, api):
        admin_user = User.objects.create_superuser("admin@test.com", "pass")
        admin_user.save()
        token = Token.objects.create(user=admin_user)
        _api = APIClient()
        _api.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        connection = RasaConversation.objects.create(conversation=conversation, domain=TEST_DOMAIN)
        connection_id = connection.id
        path = BASE_URL + f"/rasa-conversations/{connection_id}/delete-connection/"
        response = _api.get(path)

        assert response.status_code == 200
        assert not RasaConversation.objects.filter(id=connection_id).exists()

    def test_author_delete_connection(self, conversation, api):
        token = Token.objects.create(user=conversation.author)
        _api = APIClient()
        _api.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        connection = RasaConversation.objects.create(conversation=conversation, domain=TEST_DOMAIN)
        connection_id = connection.id
        path = BASE_URL + f"/rasa-conversations/{connection_id}/delete-connection/"
        response = _api.get(path)

        assert response.status_code == 200
        assert not RasaConversation.objects.filter(id=connection_id).exists()

    def test_try_other_user_delete_connection(self, conversation, api):
        user = User.objects.create(
            name="User",
            email="email@email.com",
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        user.save()
        token = Token.objects.create(user=user)
        _api = APIClient()
        _api.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        connection = RasaConversation.objects.create(conversation=conversation, domain=TEST_DOMAIN)
        connection_id = connection.id
        path = BASE_URL + f"/rasa-conversations/{connection_id}/delete-connection/"

        with pytest.raises(PermissionError):
            _api.get(path)
            assert RasaConversation.objects.filter(id=connection_id).exists()

    def test_try_unlogged_delete_connection(self, conversation, api):
        _api = APIClient()
        connection = RasaConversation.objects.create(conversation=conversation, domain=TEST_DOMAIN)
        connection_id = connection.id
        path = BASE_URL + f"/rasa-conversations/{connection_id}/delete-connection/"

        with pytest.raises(PermissionError):
            _api.get(path)
            assert RasaConversation.objects.filter(id=connection_id).exists()
