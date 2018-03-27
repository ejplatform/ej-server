from django.apps import AppConfig

# from .badges import UserCreatedBadge, UserProfileFilledBadge
# from pinax.badges.registry import badges


class GamificationConfig(AppConfig):
    name = 'ej.gamification'

    def ready(self):
        import ej.gamification.badges
        import ej.gamification.signals
