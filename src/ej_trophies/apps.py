from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class EjTrophiesConfig(AppConfig):
    name = 'ej_trophies'
    verbose_name = _('Trophies')
    api = None

    def ready(self):
        from . import api
        self.api = api
