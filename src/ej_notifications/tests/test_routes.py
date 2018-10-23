import pytest

from ej_notifications import routes
from ej_users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user('email@server.com', 'password')


class TestRoute:
    def test_index(self, rf, user):
        request = rf.get('', {})
        request.user = user
        response = routes.index(request)
        assert response == {
            'content_title': 'List of notifications',
            'user': user,
            'notifications': ['hello', 'world']
        }

    def test_cluster(self, rf, user):
        request = rf.get('', {})
        request.user = user
        response = routes.clusters(request)
        assert response == {
            'user': user,
        }