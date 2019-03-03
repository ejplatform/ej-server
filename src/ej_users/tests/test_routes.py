from ej.testing import UrlTester
from ej_users import routes
from ej_users.models import User
from ej_users.mommy_recipes import UserRecipes


class TestRoutes(UserRecipes, UrlTester):
    public_urls = [
        '/register/',
        '/login/',
        '/recover-password/',
    ]
    user_urls = [
        # '/account/logout/', -- returns error 500, so we use specific tests
        '/profile/account/remove/',
    ]

    #
    # Login
    #
    def test_invalid_login(self, db, rf, anonymous_user):
        credentials = {'email': 'email@server.com', 'password': '1234'}
        request = rf.post('/login/', credentials)
        request.user = anonymous_user
        ctx = routes.login(request)
        assert ctx['form'].errors

    def test_successful_login(self, user_client, user_db):
        user_db.set_password('1234')
        credentials = {'email': user_db.email, 'password': '1234'}
        user_client.post('/login/', data=credentials)
        assert user_client.session['_auth_user_id'] == str(user_db.pk)

    #
    # Logout
    #
    def test_logout(self, user_client):
        assert '_auth_user_id' in user_client.session
        user_client.post('/account/logout/')
        assert '_auth_user_id' not in user_client.session

    def test_logout_fails_with_anonymous_user(self, client):
        response = client.post('/account/logout/')
        assert response.status_code == 500

    def test_logout_fails_with_get(self, client):
        response = client.get('/account/logout/')
        assert response.status_code == 500

    #
    # Register
    #
    def test_register_route(self, client, db):
        response = client.post('/register/', data={'name': 'something'})
        assert response.status_code == 200

    def test_register_valid_fields(self, client, db):
        response = client.post('/register/', data={
            'name': "Turanga Leela",
            'email': "leela@example.com",
            'password': "pass123",
            'password_confirm': 'pass123'
        }, follow=True)
        user = User.objects.get(email="leela@example.com")
        assert client.session['_auth_user_id'] == str(user.pk)
        self.assert_redirects(response, '/conversations/', 302, 200)

    #
    # Reset Password
    #
    def test_get_change_password(self, db, token, rf):
        user = token.user
        request = rf.get('', {})
        response = routes.reset_password(request, token)
        assert response['user'] == user
        assert response['form']
        assert not response['is_expired']

    def test_post_matching_passwords(self, db, token, user_db, rf):
        token.user = user_db
        token.save()
        request = rf.post('', {'new_password': 'pass', 'new_password_confirm': 'pass'})
        response = routes.reset_password(request, token)
        assert response.status_code == 302

    def test_post_invalid_change_password(self, db, token, rf):
        user = token.user
        request = rf.post('', {'new_password': 'pass123', 'new_password_confirm': 'pass'})
        response = routes.reset_password(request, token)
        assert response['user'] == user
        assert response['form']
        assert not response['is_expired']
