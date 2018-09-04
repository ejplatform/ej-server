from ej.testing import UrlTester


class TestRoutes(UrlTester):
    user_urls = [
        '/profile/',
        '/profile/edit/',
    ]

    def test_comments_filter(self, client, db):
        response = client.get('/profile/comments/bad-slug/')
        assert response.status_code == 404
