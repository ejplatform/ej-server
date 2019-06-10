from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EjGamificationConfig(AppConfig):
    name = "ej_gamification"
    verbose_name = _("Gamification")
    signals = None

    def ready(self):
        from . import signals

        self.signals = vars(signals)
