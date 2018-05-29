from boogie.router import Router

urlpatterns = Router(
    template='ej_gamification/{name}.jinja2',
    login=True,
)


@urlpatterns.route('badges/')
def badges(request):
    user = request.user
    return {
        'user': user,
        'badges': user.badges.all(),
    }


@urlpatterns.route('leaderboard/')
def leaderboard(request):
    user = request.user
    return {
        'user': user,
    }


@urlpatterns.route('powers/')
def powers(request):
    user = request.user
    return {
        'user': user,
    }


@urlpatterns.route('quests/')
def quests(request):
    user = request.user
    return {
        'user': user,
    }
