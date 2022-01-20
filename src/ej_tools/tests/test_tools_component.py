from ej_conversations.mommy_recipes import ConversationRecipes

from ej_tools.forms import ConversationComponentForm
from ej_tools.models import ConversationComponent
from ej_tools.tests import HTTP_HOST
from ej_tools.views import opinion_component
from django.test import Client

ConversationRecipes.update_globals(globals())


class TestConversationComponentModel:
    def test_conversation_component_get_props_with_register_auth(self):
        form = ConversationComponentForm({"authentication_type": "register", "theme": "icd"})
        component = ConversationComponent(form)
        props = component.get_props()
        assert props == "theme=icd"

    def test_conversation_component_get_props_with_empty_form(self):
        form = ConversationComponentForm({"authentication_type": "", "theme": ""})
        component = ConversationComponent(form)
        props = component.get_props()
        assert props == "theme= authenticate-with=register"


class TestConversationComponentForm:
    def test_conversation_component_valid_form(self):
        form = ConversationComponentForm({"authentication_type": "register", "theme": "icd"})
        assert form.is_valid()


class TestComponentConversationRoute(ConversationRecipes):
    def test_post_component_conversation_valid_form(self, mk_conversation):
        conversation = mk_conversation()
        client = Client()
        client.force_login(conversation.author)

        response = client.post(
            conversation.patch_url("conversation-tools:opinion-component"),
            {"authentication_type": "register", "theme": "icd"},
            HTTP_HOST=HTTP_HOST,
        )

        assert response.context["conversation_component"].get_props() == "theme=icd"
        assert response.context["form"].is_valid()
        assert response.context["conversation"].id == conversation.id

    def test_post_votorantim_conversation_valid_form(self, mk_conversation):
        conversation = mk_conversation()
        client = Client()
        client.force_login(conversation.author)

        response = client.post(
            conversation.patch_url("conversation-tools:opinion-component"),
            {"authentication_type": "mautic", "theme": "votorantim"},
            HTTP_HOST=HTTP_HOST,
        )

        assert response.context["conversation_component"].get_props() == "theme=votorantim"
        assert response.context["form"].is_valid()
        assert response.context["conversation"].id == conversation.id

    def test_post_icd_conversation_valid_form(self, mk_conversation):
        conversation = mk_conversation()
        client = Client()
        client.force_login(conversation.author)

        response = client.post(
            conversation.patch_url("conversation-tools:opinion-component"),
            {"authentication_type": "analytics", "theme": "icd"},
            HTTP_HOST=HTTP_HOST,
        )

        assert response.context["conversation_component"].get_props() == "theme=icd"
        assert response.context["form"].is_valid()
        assert response.context["conversation"].id == conversation.id
