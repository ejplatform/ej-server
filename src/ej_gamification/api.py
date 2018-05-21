import ej_gamification.api_views


def register(router):
    router.register('badges', ej_gamification.api_views.BadgeViewSet, base_name='badges')
