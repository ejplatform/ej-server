from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EjDatavizConfig(AppConfig):
    name = 'ej_dataviz'
    verbose_name = _('Visualization')
    rules = None
    roles = None

    def ready(self):
        from . import rules, roles
        self.rules = rules
        self.roles = roles
