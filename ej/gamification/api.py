import ej.gamification.api_views


def register(router):
    router.register('badges', ej.gamification.api_views.BadgeViewSet, base_name='badges')
