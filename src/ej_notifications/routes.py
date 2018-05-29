from boogie.router import Router

urlpatterns = Router(
    login=True,
    template='ej_notifications/{name}.jinja2',
)


@urlpatterns.route()
def index(request):
    user = request.user
    return {
        'user': user,
        'notifications': user.notifications.unseen(),
    }


@urlpatterns.route('history/')
def clusters(request):
    user = request.user
    return {
        'user': user,
        'notifications': user.notifications.seen(),
    }
