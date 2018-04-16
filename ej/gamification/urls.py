from django.conf.urls import url

from . import views

urlpatterns = [
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

app_name = 'gamification'
