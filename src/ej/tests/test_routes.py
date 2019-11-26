from ej.testing import UrlTester
from ej import routes
from django.contrib.auth.models import AnonymousUser
from constance import config


class TestBasicUrls(UrlTester):
    # Urls visible to every one (even without login)
    public_urls = ["/start/"]


class TestViews:
    def test_index_route_logged_user(self, rf, db, user):
        request = rf.get("", {})
        user.save()
        request.user = user
        response = routes.index(request)
        assert response.status_code == 302
        assert response.url == config.EJ_USER_HOME_PATH

    def test_index_anonymous_user(self, rf):
        request = rf.get("", {})
        request.user = AnonymousUser()
        response = routes.index(request)
        assert response.status_code == 302
        assert response.url == config.EJ_ANONYMOUS_HOME_PATH
