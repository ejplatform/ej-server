import pytest
from django.http import Http404

from ej.testing import UrlTester
from ej_profiles import routes


class TestRoutes(UrlTester):
    user_urls = [
        '/profile/',
        '/profile/edit/',
        '/profile/conversations/'
    ]

    def test_comments_filter_bad_slug(self, rf, db, mk_user):
        request = rf.get('', {})
        request.user = mk_user
        with pytest.raises(Http404):
            routes.comments_tab(request, 'bad-slug')

    def test_comments_filter_approve(self, rf, db, mk_user):
        user = mk_user()
        request = rf.get('', {})
        request.user = user
        response = routes.comments_tab(request, 'approved')
        assert response['user'] == user
        assert not response['comments']
        assert not response['stats']

    def test_comments(self, rf, db, mk_user):
        user = mk_user()
        request = rf.get('', {})
        request.user = user
        response = routes.comments_list(request)
        assert response['user'] == user
        assert not response['comments']
        assert not response['stats']
