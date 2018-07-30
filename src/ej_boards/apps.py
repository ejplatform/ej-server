from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EjBoardsConfig(AppConfig):
    name = 'ej_boards'
    verbose_name = _('Boards')
    rules = None
    api = None

    def ready(self):
        from . import rules, api

        self.rules = rules
        self.api = api
