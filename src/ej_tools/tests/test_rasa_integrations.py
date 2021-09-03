import pytest
from django.db import IntegrityError
from django.utils.translation import ugettext as _
from django.test import TestCase
from django.test.client import Client

from ej_conversations.mommy_recipes import ConversationRecipes
from ej_tools.models import RasaConversation
from ej_tools.forms import RasaConversationForm
from ej_tools.routes import rasa

ConversationRecipes.update_globals(globals())

TEST_DOMAIN = "https://domain.com.br"


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
        print(form.errors.keys())
        assert (
            _("Rasa conversation with this Conversation and Domain already exists.")
            == form.errors["__all__"][0]
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
    def test_post_rasa_conversation_valid_form(self, db, mk_conversation, rf, admin):
        conversation = mk_conversation()

        request = rf.post(
            conversation.get_absolute_url() + "/tools/rasa",
            {"conversation": conversation.id, "domain": "http://domain.com.br"},
        )
        request.user = admin
        response = rasa(request, conversation, None)
        assert response["conversation_rasa_connections"]
        assert response["conversation_rasa_connections"][0].domain == "http://domain.com.br"
        assert response["conversation_rasa_connections"][0].conversation.id == conversation.id

    def test_post_rasa_conversation_invalid_form(self, db, mk_conversation, rf, admin):
        conversation = mk_conversation()

        request = rf.post(
            conversation.get_absolute_url() + "/tools/rasa",
            {"conversation": conversation.id, "domain": "nope"},
        )
        request.user = admin
        response = rasa(request, conversation, None)
        assert not response["conversation_rasa_connections"]
        assert not response["form"].is_valid()

    def test_post_rasa_conversation_invalid_permission_form(self, db, mk_conversation, rf, user):
        conversation = mk_conversation()

        request = rf.post(
            conversation.get_absolute_url() + "/tools/rasa",
            {"conversation": conversation.id, "domain": "http://domain.com.br"},
        )
        request.user = user
        with pytest.raises(PermissionError):
            rasa(request, conversation, None)


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
