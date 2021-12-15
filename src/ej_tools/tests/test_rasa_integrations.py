import pytest
import random
from ej_users.models import User
from django.db import IntegrityError
from django.utils.translation import ugettext as _
from django.test.client import Client
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_tools.models import RasaConversation, WebchatHelper
from ej_tools.forms import RasaConversationForm

ConversationRecipes.update_globals(globals())

TEST_DOMAIN = "https://domain.com.br"
HTTP_HOST = "docs.djangoproject.dev:8000"


class TestRasaConversation(ConversationRecipes):
    def test_creation_rasa_conversation(self, db, mk_conversation):
        conversation = mk_conversation()
        rasa_conversation = RasaConversation.objects.create(conversation=conversation, domain=TEST_DOMAIN)
        assert rasa_conversation.id is not None

    def test_creation_duplicated_rasa_conversation(self, db, mk_conversation):
        conversation = mk_conversation()
        rasa_conversation = RasaConversation.objects.create(conversation=conversation, domain=TEST_DOMAIN)
        assert rasa_conversation.id is not None
        with pytest.raises(IntegrityError):
            RasaConversation.objects.create(conversation=conversation, domain=TEST_DOMAIN)


class TestRasaConversationForm(ConversationRecipes):
    def test_rasa_conversation_valid_form(self, db, mk_conversation):
        conversation = mk_conversation()
        form = RasaConversationForm({"domain": "http://another.com", "conversation": conversation.id})
        assert form.is_valid()

    def test_rasa_conversation_invalid_form(self, db, mk_conversation):
        conversation = mk_conversation()
        form = RasaConversationForm({"domain": "notadomain"})
        assert not form.is_valid()
        assert _("Enter a valid URL.") == form.errors["domain"][0]

    def test_rasa_conversation_form_exists(self, db, mk_conversation):
        conversation = mk_conversation()
        RasaConversation.objects.create(conversation=conversation, domain="https://domain.com.br")
        form = RasaConversationForm({"domain": TEST_DOMAIN, "conversation": conversation.id})
        assert not form.is_valid()
        assert (
            _("Rasa conversation with this Conversation and Domain already exists.")
            == form.errors["domain"][0]
        )

    def test_rasa_conversation_form_domain_already_in_use(self, db, mk_conversation, mk_user):
        conversation1 = mk_conversation()
        user = mk_user(email="test@domain.com")
        conversation2 = mk_conversation(author=user)
        RasaConversation.objects.create(conversation=conversation1, domain="https://domain.com.br")
        form = RasaConversationForm({"domain": TEST_DOMAIN, "conversation": conversation2.id})
        assert (
            _("Site already integrated with conversation Conversation, try another url.")
            == form.errors["domain"][0]
        )

    def test_rasa_conversation_invalid_number_of_domains(self, db, mk_conversation):
        conversation = mk_conversation()
        RasaConversation.objects.create(conversation=conversation, domain="https://domain1.com.br/")
        RasaConversation.objects.create(conversation=conversation, domain="https://domain2.com.br/")
        RasaConversation.objects.create(conversation=conversation, domain="https://domain3.com.br/")
        RasaConversation.objects.create(conversation=conversation, domain="https://domain4.com.br/")
        RasaConversation.objects.create(conversation=conversation, domain="https://domain5.com.br/")
        form = RasaConversationForm({"domain": "https://domain6.com.br/", "conversation": conversation.id})
        assert not form.is_valid()
        assert _("a conversation can have a maximum of five domains") == form.errors["__all__"][0]


class TestRasaConversationFormRoute(ConversationRecipes):
    def test_post_rasa_conversation_valid_form(self, db, mk_conversation):
        conversation = mk_conversation()

        client = Client()
        admin = User.objects.create_superuser("myemail@test.com", "password")
        client.force_login(user=admin)
        response = client.post(
            conversation.get_absolute_url() + "tools/chatbot/webchat",
            {"conversation": conversation.id, "domain": TEST_DOMAIN},
            HTTP_HOST=HTTP_HOST,
        )

        assert response.status_code == 200
        assert RasaConversation.objects.filter(conversation=conversation, domain=TEST_DOMAIN).exists()

    def test_post_rasa_conversation_invalid_form(self, db, mk_conversation):
        conversation = mk_conversation()

        client = Client()
        admin = User.objects.create_superuser("myemail@test.com", "password")
        client.force_login(user=admin)
        invalid_domain = "nope"
        response = client.post(
            conversation.get_absolute_url() + "tools/chatbot/webchat",
            {"conversation": conversation.id, "domain": invalid_domain},
            HTTP_HOST=HTTP_HOST,
        )
        response_content = response.content.decode("utf-8")
        assert _("Enter a valid URL") in response_content
        assert not RasaConversation.objects.filter(
            conversation=conversation, domain=invalid_domain
        ).exists()

    def test_post_rasa_conversation_invalid_permission_form(self, db, mk_conversation):
        conversation = mk_conversation()
        client = Client()
        with pytest.raises(PermissionError):
            client.post(
                conversation.get_absolute_url() + "tools/chatbot/webchat",
                {"conversation": conversation.id, "domain": "http://domain.com.br"},
                HTTP_HOST=HTTP_HOST,
            )


class TestRasaConversationIntegrationsAPI(ConversationRecipes):
    BASE_URL = "/api/v1"

    def test_conversations_endpoint(self, db, mk_conversation):
        conversation = mk_conversation()
        TEST_DOMAIN = "https://domain.com.br"

        RasaConversation.objects.create(conversation=conversation, domain=TEST_DOMAIN)
        path = self.BASE_URL + f"/rasa-conversations/integrations/?domain={TEST_DOMAIN}"
        client = Client()
        response = client.get(path)
        assert response.status_code == 200
        assert conversation.text == response.data.get("conversation").get("text")
        assert conversation.id == response.data.get("conversation").get("id")
        assert TEST_DOMAIN == response.data.get("domain")

    def test_no_integration_api(self, db):
        url = self.BASE_URL + f"/rasa-conversations/integrations/?domain={TEST_DOMAIN}"
        client = Client()
        response = client.get(url)
        assert response.status_code == 200
        assert response.data == {}


class TestWebchatHelper:
    EJ_POSSIBLE_URLS = [
        "http://localhost:8000",
        "https://ejplatform.pencillabs.com.br/",
        "https://www.ejplatform.org",
    ]

    def test_get_current_available_instance(self):
        current_host = random.choice(TestWebchatHelper.EJ_POSSIBLE_URLS)
        rasa_instance_url = WebchatHelper.get_rasa_domain(current_host)
        assert rasa_instance_url
        assert rasa_instance_url == WebchatHelper.AVAILABLE_ENVIRONMENT_MAPPING.get(current_host)

    def test_if_instance_not_available(self):
        rasa_instance_url = WebchatHelper.get_rasa_domain(HTTP_HOST)
        assert not rasa_instance_url
