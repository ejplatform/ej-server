from ej.testing import UrlTester
from ej_users import routes
from ej_users.models import User
from ej_users.mommy_recipes import UserRecipes


class TestRoutes(UserRecipes, UrlTester):
    public_urls = [
        "/register/",
        "/login/",
        "/recover-password/",
        # '/recover-password/<token>' -- requires special initialization
    ]
    user_urls = [
        "/account/",
        "/account/logout/",
        "/account/remove/",
        "/account/manage-email/",
        "/account/change-password/",
    ]

    # Login / logout
    def test_invalid_login(self, db, rf, anonymous_user):
        credentials = {"email": "email@server.com", "password": "1234"}
        request = rf.post("/login/", credentials)
        request.user = anonymous_user
        ctx = routes.login(request)
        assert ctx["form"].errors

    def test_successful_login(self, user_client, user_db):
        user_db.set_password("1234")
        credentials = {"email": user_db.email, "password": "1234"}
        user_client.post("/login/", data=credentials)
        assert user_client.session["_auth_user_id"] == str(user_db.pk)

    def test_logout(self, user_client):
        assert "_auth_user_id" in user_client.session
        user_client.post("/account/logout/")
        assert "_auth_user_id" not in user_client.session

    # Register
    def test_register_valid_user(self, client, db):
        response = client.post(
            "/register/",
            data={
                "name": "Turanga Leela",
                "email": "leela@example.com",
                "password": "pass123",
                "password_confirm": "pass123",
            },
            follow=True,
        )
        user = User.objects.get(email="leela@example.com")
        assert client.session["_auth_user_id"] == str(user.pk)
        self.assert_redirects(response, "/leelaexamplecom/conversations/tour/", 302, 200)

    def test_registration_auth_valid_user(self, client, db):
        client.post(
            "/api/v1/users/",
            data={
                "name": "David Silva",
                "email": "david@example.com",
                "password": "pass123",
                "password_confirm": "pass123",
                "metadata": {"analytics_id": "GA.1.1234", "mautic_id": 123456},
            },
            content_type="application/json",
        )
        user = User.objects.get(email="david@example.com")
        assert user.metadata_set.first().analytics_id == "GA.1.1234"
        assert user.metadata_set.first().mautic_id == 123456

    # Recover password
    def test_recover_user_password(self, db, user, client):
        user.save()
        response = client.post("/recover-password/", data={"email": user.email})

        # Fetch token url and go to token page saving new password
        token_url = response.context[0]["url"].partition("/testserver")[2]
        client.post(token_url, data={"password": "12345", "password_confirm": "12345"})

        # Check credentials
        client.login(email=user.email, password="12345")
        assert client.session["_auth_user_id"] == str(user.pk)

    # Recover password
    def test_remove_account(self, user_client, user_db):
        client, user = user_client, user_db
        client.post("/account/remove/", data={"confirm": "true", "email": user.email})
        updated_user = User.objects.get(id=user.id)
        assert updated_user.email.endswith("@deleted-account")

    def test_registration_rest_auth_valid_user(self, client, db):
        response = client.post(
            "/api/v1/users/",
            data={
                "name": "jonatas Silva",
                "email": "jonatas@example.com",
                "password": "pass123",
                "password_confirm": "pass123",
                "metadata": {"analytics_id": "GA.1.1234", "mautic_id": 123456},
            },
            content_type="application/json",
        )
        user = User.objects.get(email="jonatas@example.com")
        assert user.metadata_set.first().analytics_id == "GA.1.1234"
        assert user.metadata_set.first().mautic_id == 123456

    def test_registration_rest_auth_incorrect_confirm_password(self, client, db):
        response = client.post(
            "/api/v1/users/",
            data={
                "name": "jonatas Silva",
                "email": "jonatassilva@example.com",
                "password": "pass123",
                "password_confirm": "pass1234",
                "metadata": {"analytics_id": "GA.1.1234", "mautic_id": 123456},
            },
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_registration_rest_auth_missing_password(self, client, db):
        response = client.post(
            "/api/v1/users/",
            data={
                "name": "jonatas Silva",
                "email": "jonatasgomes@mail.com",
                "password_confirm": "pass123",
                "metadata": {"analytics_id": "GA.1.1234", "mautic_id": 123456},
            },
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_user_endpoint_post_with_already_created_user(self, client, db):
        User.objects.create_user("user@user.com", "password")
        response = client.post(
            "/api/v1/users/",
            data={
                "email": "user@user.com",
            },
            content_type="application/json",
        )
        assert "token" in response.content.decode()
        assert response.status_code == 200
