from ej_users.forms import RegistrationForm, LoginForm, ResetPasswordForm


class TestRegistrationForm:
    def test_valid_data(self, db):
        form = RegistrationForm({
            'name': "Turanga Leela",
            'email': "leela@example.com",
            'password': "pass123",
            'password_confirm': 'pass123'
        })
        assert form.is_valid()
        registered_user = form.save()
        assert registered_user.name == "Turanga Leela"
        assert registered_user.email == "leela@example.com"

    def test_blank_data(self, db):
        form = RegistrationForm({})
        required = ['This field is required.']
        assert not form.is_valid()
        assert form.errors == {
            'name': required,
            'email': required,
            'password': required,
            'password_confirm': required,
        }

    def test_not_matching_passwords(self, db):
        form = RegistrationForm({
            'name': "Turanga Leela",
            'email': "leela@example.com",
            'password': "pass123",
            'password_confirm': 'wrong123'
        })
        assert form.errors == {
            'password_confirm': ['Passwords do not match'],
        }
        assert not form.is_valid()


class TestLoginForm:
    def test_valid_data(self, db):
        form = LoginForm({
            'email': "leela@example.com",
            'password': "pass123",
        })
        assert form.is_valid()

    def test_blank_data(self):
        form = LoginForm({})
        required = ['This field is required.']
        assert not form.is_valid()
        assert form.errors == {
            'email': required,
            'password': required,
        }


class TestResetPasswordForm:

    def test_create_new_password(self):
        form = ResetPasswordForm({
            'new_password': '123',
            'new_password_confirm': '123',
        })
        assert form.is_valid()

    def test_not_matching_passwords(self, db):
        form = ResetPasswordForm({
            'new_password': "pass123",
            'new_password_confirm': 'wrong123',
        })
        assert form.errors == {
            'new_password_confirm': ['Passwords do not match'],
        }
        assert not form.is_valid()
