from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EjGamificationConfig(AppConfig):
    name = "ej_gamification"
    verbose_name = _("Gamification")
    signals = None
    roles = None

    def ready(self):
        from . import signals
        from . import roles

        self.signals = signals
        self.roles = roles
