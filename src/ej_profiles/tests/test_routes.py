from ej.testing import UrlTester


class TestRoutes(UrlTester):
    user_urls = [
        '/profile/',
        '/profile/edit/',
        '/profile/comments/',
        '/profile/comments/rejected/',
        '/profile/comments/approved/',
        '/profile/comments/pending/',
    ]


def test_comments_filter(client, db):
    response = client.get('/profile/comments/test/')
    assert response.status_code == 404
