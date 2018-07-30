import logging

import pytest


class UrlTester:
    """
    Base test class that checks the response code for specific urls in an app.
    """
    public_urls = []
    user_urls = []
    owner_urls = []

    @pytest.fixture
    def data(self):
        return None

    def test_anonymous_user_can_access_urls(self, client, caplog, data):
        caplog.set_level(logging.CRITICAL, logger='django')
        check_urls(client, self.public_urls, 200)

    def test_urls_that_requires_user_login(self, client, user_db, caplog):
        urls = self.user_urls
        caplog.set_level(logging.CRITICAL, logger='django')

        check_urls(client, urls, 404)

        client.force_login(user_db)
        check_urls(client, urls, 200)

    def test_urls_accessible_only_by_author_or_admin(self, client, user_db,
                                                     author_db, caplog):
        urls = self.user_urls
        caplog.set_level(logging.CRITICAL, logger='django')

        check_urls(client, urls, 404)

        client.force_login(user_db)
        check_urls(client, urls, 404)

        client.force_login(author_db)
        check_urls(client, urls, 200)


def check_urls(client, urls, code=200):
    """
    Check all urls on the url list.
    """
    for url in urls:
        check_url(client, url, code)


def check_url(client, url, code):
    """
    Check if client responds to given url with the provided status code.
    """
    try:
        response = client.get(url)
    except Exception as ex:
        print('Error loading url: %s' % url)
        raise RuntimeError(f'{ex.__class__.__name__}: {ex}')
    assert response.status_code == code, f'url: {url}'
