from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EjConversationsConfig(AppConfig):
    name = 'ej_conversations'
    verbose_name = _('Conversations')
    rules = None
    api = None
    components = None

    def ready(self):
        from . import rules, api, components

        self.rules = rules
        self.api = api
        self.components = components
