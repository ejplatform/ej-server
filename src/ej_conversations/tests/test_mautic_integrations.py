import pytest
from django.utils.translation import ugettext as _

from ej_conversations.mommy_recipes import ConversationRecipes
from ej_conversations.models import ConversationMautic
from ej_conversations.tools.forms import MauticConversationForm

ConversationRecipes.update_globals(globals())

TEST_DOMAIN = "https://domain.com.br"


class TestMauticConversationForm(ConversationRecipes):
    def test_mautic_conversation_valid_form(self, db, mk_conversation):
        conversation = mk_conversation()
        form = MauticConversationForm(
            {
                "user_name": "username",
                "url": TEST_DOMAIN,
                "conversation": conversation.id,
                "password": "password",
            }
        )
        print(form)
        assert form.is_valid()

    def test_mautic_conversation_invalid_form(self, db, mk_conversation):
        conversation = mk_conversation()
        form = MauticConversationForm({"url": "invalidurl"}, initial={"conversation": conversation})
        assert not form.is_valid()
        assert _("Enter a valid URL.") == form.errors["url"][0]
