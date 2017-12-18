from rest_framework.routers import SimpleRouter
from django.conf.urls import url

from . import views

router = SimpleRouter()

router.register('badges', views.BadgeViewSet, base_name='badges')
# router.register('points-leaderboard', views.PointsLeaderBoardView.as_view(), base_name='points-leaderboard')

# urlpatterns = router.urls

urlpatterns = [
    # url(
    #     regex=r'^badges/$',
    #     view=views.BadgeViewSet.as_view(),
    #     name='badges-list'
    # ),
    url(
        regex=r'^points-leaderboard/$',
        view=views.PointsLeaderBoardView.as_view(),
        name='points-leaderboard'
    ),
    url(
        regex=r'^awarded-points/$',
        view=views.AwardedPointsView.as_view(),
        name='awarded-points'
    ),
]

urlpatterns.extend(router.urls)
