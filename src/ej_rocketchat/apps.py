from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EJRocketchatConfig(AppConfig):
    name = 'ej_rocketchat'
    verbose_name = _('Rocket chat integration')
    signals = None

    def ready(self):
        from . import signals

        self.signals = signals
