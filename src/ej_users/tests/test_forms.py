from boogie.testing.mock import assume_unique
from ej_users.forms import RegistrationForm, LoginForm, ResetPasswordForm


class TestRegistrationForm:
    @assume_unique()
    def test_valid_data(self):
        form = RegistrationForm({
            'name': "Turanga Leela",
            'email': "leela@example.com",
            'password': "pass123",
            'password_confirm': 'pass123'
        })
        assert form.is_valid()
        user = form.save(commit=False)
        assert user.name == "Turanga Leela"
        assert user.email == "leela@example.com"

    @assume_unique()
    def test_blank_data(self):
        form = RegistrationForm({})
        required = ['This field is required.']
        assert not form.is_valid()
        assert form.errors == {
            'name': required,
            'email': required,
            'password': required,
            'password_confirm': required,
        }

    @assume_unique()
    def test_not_matching_passwords(self):
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
    def test_valid_data(self):
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

    def test_not_matching_passwords(self):
        form = ResetPasswordForm({
            'new_password': "pass123",
            'new_password_confirm': 'wrong123',
        })
        assert form.errors == {
            'new_password_confirm': ['Passwords do not match'],
        }
        assert not form.is_valid()
