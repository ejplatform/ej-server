from ej.testing import UrlTester


class TestRoutes(UrlTester):
    user_urls = [
        '/config/',
        '/config/info/',
        '/config/fragment/',
        '/config/fragment/test/',
        '/config/styles/',
    ]
