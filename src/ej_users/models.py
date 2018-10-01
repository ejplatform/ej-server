from django.db import models
from django.utils.translation import ugettext_lazy as _

from boogie import rules
from boogie.apps.users.models import AbstractUser
from boogie.rest import rest_api
from .manager import UserManager
from .utils import random_name
from django.utils import timezone
from datetime import datetime
from secrets import token_urlsafe


@rest_api(['id', 'display_name'])
class User(AbstractUser):
    """
    Default user model for EJ platform.
    """

    display_name = models.CharField(
        _('Display name'),
        max_length=140,
        unique=True,
        default=random_name,
        help_text=_(
            'A randomly generated name used to identify each user.'
        ),
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=('Your e-mail address')
    )

    objects = UserManager()

    @property
    def username(self):
        return self.email.replace('@', '__')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    @property
    def profile(self):
        profile = rules.get_value('auth.profile')
        return profile(self)

    class Meta:
        swappable = 'AUTH_USER_MODEL'


class Token (models.Model):

    url_token = models.CharField(
        ('user token'),
        unique=True,
        max_length=50,
        null=True,
    )

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
    )

    date_time = models.DateTimeField(
        auto_now=True,
    )

    @property
    def is_expired(self):
        time_now = datetime.now(timezone.utc)
        return (time_now - self.date_time).total_seconds() > 600

    def generate_token(self):
        self.url_token = token_urlsafe(30)
