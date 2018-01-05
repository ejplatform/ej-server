from django.apps import AppConfig

# from .badges import UserCreatedBadge, UserProfileFilledBadge
# from pinax.badges.registry import badges


class GamificationConfig(AppConfig):
    name = 'pushtogether.gamification'

    def ready(self):
        import pushtogether.gamification.badges
        import pushtogether.gamification.signals
    #     badges.register(UserCreatedBadge)
    #     badges.register(UserProfileFilledBadge)
