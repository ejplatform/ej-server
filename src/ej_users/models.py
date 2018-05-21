from boogie.apps.users.models import AbstractUser
from .manager import UserManager


class User(AbstractUser):
    """
    Default user model for EJ platform.
    """

    objects = UserManager()

    class Meta:
        swappable = 'AUTH_USER_MODEL'
