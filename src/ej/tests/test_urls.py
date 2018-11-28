from django.contrib.auth import get_user_model

from boogie.testing.pytest import CrawlerTester, UrlTester

User = get_user_model()


class MakeUserMixin:
    def make_user(self, username, **kwargs):
        return User.objects.create_user(name=username, **kwargs)


class TestUserCrawl(MakeUserMixin, CrawlerTester):
    start = '/'
    user = 'user'


class TestAuthorCrawl(MakeUserMixin, CrawlerTester):
    start = '/'
    user = 'author'


class TestUrls(MakeUserMixin, UrlTester):
    urls = {
        None: [
            '/',
            '/home/',
            '/conversations/'
        ],
    }
