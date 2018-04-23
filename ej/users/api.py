import ej.users.api_views


def register(router):
    router.register(r'users', ej.users.api_views.UserViewSet)