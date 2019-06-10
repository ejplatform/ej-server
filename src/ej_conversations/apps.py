from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _


class EjConversationsConfig(AppConfig):
    name = "ej_conversations"
    verbose_name = _("Conversations")
    rules = None
    api = None
    roles = None

    def ready(self):
        from . import rules, api, roles
        from .models.conversation import patch_user_model

        self.rules = rules
        self.api = api
        self.roles = roles
        patch_user_model(get_user_model())
