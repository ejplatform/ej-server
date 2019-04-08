default_app_config = "ej_users.apps.EjUsersConfig"


def password_reset_token(user, commit=True):
    """
    Create a new password token for user.
    """
    from ej_users.models import PasswordResetToken

    token = PasswordResetToken(user=user)
    if commit:
        token.save()
    return token
