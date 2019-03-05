from django.apps import AppConfig


class EjGamificationConfig(AppConfig):
    name = 'ej_gamification'
    verbose_name = 'Gamification'
    signals = None
    badges = None

    def ready(self):
        # from . import badges
        # from . import signals
        # self.signals = vars(signals)
        # self.badges = vars(badges)
        pass
