from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EjReportsConfig(AppConfig):
    name = 'ej_reports'
    verbose_name = _('Reports')
    rules = None

    def ready(self):
        from . import rules
        self.rules = rules
