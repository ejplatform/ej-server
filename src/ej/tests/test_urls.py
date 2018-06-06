class TestBasicUrls:
    # Urls visible to every one (even without login)
    public_urls = {
        # Basic login/profile related urls
        '/'
        '/login/',
        '/register/',
        '/profile/recover-password/',

    }

    # Urls that redirect to the login page for anonymous users
    login_redirect_urls = {
        '/profile/reset-password/',
        '/profile/remove/',
    }

    login_required_urls = {
        *public_urls,
        *login_redirect_urls,
    }

    def test_visible_urls_for_anonymous_user(self, db, client):
        for url in self.public_urls:
            response = client.get(url)
            assert response.status_code == 200, f'url: {url}'

    def test_url_redirects(self, db, client):
        for url in self.login_redirect_urls:
            response = client.get(url)
            assert response.status_code == 302, f'url: {url}'
