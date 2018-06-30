from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class EjUsersConfig(AppConfig):
    name = 'ej_users'
    verbose_name = _('Users')
    api = None

    def ready(self):
        from . import rules, api
        self.rules = rules
        self.api = api
