from django.apps import AppConfig


class GamificationConfig(AppConfig):
    name = 'ej.gamification'

    def ready(self):
        from ej.gamification import badges
        from ej.gamification import signals

        self.signals = vars(signals)
        self.badges = vars(badges)
