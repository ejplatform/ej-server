import logging
import typing
from pprint import pprint
import pytest

from .fixture_class import EjRecipes


class UrlTester(EjRecipes):
    """
    Base test class that checks the response code for specific urls in an app.
    """
    public_urls = []
    user_urls = []
    owner_urls = []
    success_codes = {200}
    failure_codes = {404}
    redirect_codes = {302}

    @property
    def require_login_codes(self):
        prep = as_code_set
        return {*prep(self.redirect_codes), *prep(self.success_codes)}

    @pytest.fixture
    def data(self):
        return None

    @pytest.mark.django_db
    def test_anonymous_user_can_access_urls(self, client, caplog, data):
        caplog.set_level(logging.CRITICAL, logger='django')
        check_urls(client, self.public_urls, self.success_codes)
        pprint(data)

    def test_urls_that_requires_user_login(self, client, user_db, caplog, data):
        urls = self.user_urls
        caplog.set_level(logging.CRITICAL, logger='django')
        pprint(data)

        check_urls(client, urls, self.require_login_codes)

        client.force_login(user_db)
        check_urls(client, urls, self.success_codes)

    def test_urls_accessible_only_by_author_or_admin(self, client, user_db,
                                                     author_db, data, caplog):
        urls = self.owner_urls
        caplog.set_level(logging.CRITICAL, logger='django')
        pprint(data)

        # Require login or present a failure code if user is anonymous
        check_urls(client, urls, {*as_code_set(self.redirect_codes),
                                  *as_code_set(self.failure_codes)})

        # User has no permission
        client.force_login(user_db)
        check_urls(client, urls, self.failure_codes)

        # User is author and therefore can see the page
        client.force_login(author_db)
        check_urls(client, urls, self.success_codes)


def check_urls(client, urls, code: typing.Union[int, set]):
    """
    Check all urls on the url list.
    """
    code = as_code_set(code)
    for url in urls:
        check_url(client, url, code)


def check_url(client, url, code):
    """
    Check if client responds to given url with the provided status code.
    """
    try:
        response = client.get(url)
    except Exception:
        print('Error loading url: %s' % url)
        raise
    if response.status_code not in code:
        msg = (f'bad response code for "{url}":\n'
               f'    got {response.status_code}, expected {code}')
        raise AssertionError(msg)


def as_code_set(code):
    return {code} if isinstance(code, int) else set(code)
