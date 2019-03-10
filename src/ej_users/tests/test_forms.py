from ej_users.forms import PasswordForm


class TestForms:
    def test_password_form(self):
        # Matching passwords
        form = PasswordForm({'password': '123', 'password_confirm': '123'})
        assert form.is_valid()

        # Non-matching passwords
        form = PasswordForm({'password': '123', 'password_confirm': '1234'})
        assert not form.is_valid()
