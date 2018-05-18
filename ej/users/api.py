from .api_views import UserViewSet


def register(router):
    router.register(r'users', UserViewSet)
