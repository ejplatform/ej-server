import pytest
from ej_conversations.mommy_recipes import ConversationRecipes

from ej_tools.forms import ConversationComponentForm
from ej_tools.models import ConversationComponent
from ej_tools.routes import opinion_component

ConversationRecipes.update_globals(globals())


class TestConversationComponentModel:
    def test_conversation_component_get_props_with_analytics_auth(self):
        form = ConversationComponentForm({"authentication_type": "analytics", "theme": "icd"})
        component = ConversationComponent(form)
        props = component.get_props()
        assert props == "theme=icd authenticate-with=analytics"

    def test_conversation_component_get_props_with_mautic_auth(self):
        form = ConversationComponentForm({"authentication_type": "mautic", "theme": "icd"})
        component = ConversationComponent(form)
        props = component.get_props()
        assert props == "theme=icd authenticate-with=mautic"

    def test_conversation_component_get_props_with_register_auth(self):
        form = ConversationComponentForm({"authentication_type": "register", "theme": "icd"})
        component = ConversationComponent(form)
        props = component.get_props()
        assert props == "theme=icd authenticate-with=register"

    def test_conversation_component_get_props_with_custom_theme(self):
        form = ConversationComponentForm({"authentication_type": "mautic", "theme": "votorantim"})
        component = ConversationComponent(form)
        props = component.get_props()
        assert props == "theme=votorantim authenticate-with=mautic"

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
    def test_post_component_conversation_valid_form(self, db, mk_conversation, rf):
        conversation = mk_conversation()

        request = rf.post(
            conversation.get_absolute_url() + "/tools/opinion-component",
            {"authentication_type": "register", "theme": "icd"},
        )
        response = opinion_component(request, conversation)
        assert response["conversation_component"].get_props() == "theme=icd authenticate-with=register"
        assert response["form"].is_valid()
        assert response["conversation"].id == conversation.id

    def test_post_votorantim_conversation_valid_form(self, db, mk_conversation, rf):
        conversation = mk_conversation()

        request = rf.post(
            conversation.get_absolute_url() + "/tools/opinion-component",
            {"authentication_type": "mautic", "theme": "votorantim"},
        )
        response = opinion_component(request, conversation)
        assert response["conversation_component"].get_props() == "theme=votorantim authenticate-with=mautic"
        assert response["form"].is_valid()
        assert response["conversation"].id == conversation.id

    def test_post_icd_conversation_valid_form(self, db, mk_conversation, rf):
        conversation = mk_conversation()

        request = rf.post(
            conversation.get_absolute_url() + "/tools/opinion-component",
            {"authentication_type": "analytics", "theme": "icd"},
        )
        response = opinion_component(request, conversation)
        assert response["conversation_component"].get_props() == "theme=icd authenticate-with=analytics"
        assert response["form"].is_valid()
        assert response["conversation"].id == conversation.id
