import ej.users.api_views
from . import views


def register(router):
    router.register(r'users', ej.users.api_views.UserViewSet),
    router.register(r'users/me', ej.users.api_views.UserViewSet.as_view({'get': 'retrieve'}), base_name='me'),
