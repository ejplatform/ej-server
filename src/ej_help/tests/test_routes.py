import pytest

import ej_help.utils
from ej_users.models import User
from ej_help import routes
from ej_configurations import social_icons


@pytest.fixture
def user(db):
    user = User.objects.create_user('email@server.com', 'password')
    return user


class TestRoutes:
    def test_flat_pages_route(self, db, rf, user):
        request = rf.get('', {})
        request.user = user
        route = ej_help.utils.flat_pages_route('about-us')
        response = route(request)
        assert response.status_code == 200
        assert response._content_type_for_repr == ', "text/html; charset=utf-8"'

    def test_fallback_page_with_inexistent_page(self):
        response = ej_help.utils.fallback_page('inexistent-page')
        assert response.content == 'Page inexistent-page not found'

    def test_fallback_page_with_existent_page(self):
        response = ej_help.utils.fallback_page('about-us')
        assert response.content != 'Page about-us not found'

    def test_start_route(self):
        response = routes.start()
        assert response == {}

    def test_social_route(self, db):
        response = routes.social()
        assert response == {'icons': social_icons()}
