from ej.testing import UrlTester


class TestBasicUrls(UrlTester):
    # Urls visible to every one (even without login)
    public_urls = [
        # Basic login/profile related urls
        '/start/',
        '/menu/',
        '/home/',
    ]
