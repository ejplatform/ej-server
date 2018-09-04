from boogie.router import Router

app_name = 'ej_gamification'
urlpatterns = Router(
    template=['ej_gamification/{name}.jinja2', 'generic.jinja2'],
    login=True,
)


@urlpatterns.route('badges/')
def badges(request):
    user = request.user
    return {
        'user': user,
        'badges': user.badges_earned.all(),
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
