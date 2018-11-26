from django.contrib.auth import get_user_model

from boogie.testing import crawler
from boogie.testing import url

User = get_user_model()


class MakeUserMixin:
    def make_user(self, username, **kwargs):
        return User.objects.create_user(name=username, **kwargs)


class TestCrawl(MakeUserMixin, crawler.TestCrawl):
    bases = [
        ('/', None),
        # ('/', 'user'),
        # ('/', 'author'),
        # ('/', 'admin'),
    ]


class TestUrls(MakeUserMixin, url.TestUrls):
    urls = {
        None: [
            '/',
            '/home/',
            '/conversations/'
        ],

        'user': [

        ]
    }
