from django.apps import AppConfig


class GamificationConfig(AppConfig):
    name = 'ej_gamification'

    def ready(self):
        from . import badges
        from . import signals

        self.signals = vars(signals)
        self.badges = vars(badges)
