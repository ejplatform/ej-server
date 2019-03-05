from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EjConfigurationsConfig(AppConfig):
    name = 'ej_configurations'
    verbose_name = _('Configurations')
    api = None

    def ready(self):
        from . import api
        self.api = api
