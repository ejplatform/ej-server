from ej.testing import UrlTester


class TestRoutes(UrlTester):
    public_urls = [
        '/config/fragment/test/',
        '/config/styles/',
    ]
    admin_urls = [
        '/config/',
        '/config/info/',
        '/config/fragment/',
    ]
