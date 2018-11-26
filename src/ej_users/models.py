from datetime import datetime, timedelta
from secrets import token_urlsafe

from boogie import rules
from boogie.apps.users.models import AbstractUser
from boogie.rest import rest_api
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from .manager import UserManager


def token_factory():
    return token_urlsafe(30)


@rest_api(['id'])
class User(AbstractUser):
    """
    Default user model for EJ platform.
    """

    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Your e-mail address')
    )

    objects = UserManager()

    limit_board_conversations = models.PositiveIntegerField(
        _('Limit conversations in board'),
        default=0,
        help_text=_(
            'Limit number of conversations in user board '
        ),
    )

    @property
    def username(self):
        return self.email.replace('@', '__')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    @property
    def profile(self):
        profile = rules.get_value('auth.profile')
        return profile(self)

    @property
    def notifications_options(self):
        notifications_options = rules.get_value('auth.notification_options')
        return notifications_options(self)

    class Meta:
        swappable = 'AUTH_USER_MODEL'


class PasswordResetToken(TimeStampedModel):
    """
    Expiring token for password recovery.
    """
    url = models.CharField(
        _('User token'),
        max_length=50,
        unique=True,
        default=token_factory,
    )
    is_used = models.BooleanField(default=False)
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
    )

    @property
    def is_expired(self):
        time_now = datetime.now(timezone.utc)
        return (time_now - self.created).total_seconds() > 600

    def use(self, commit=True):
        self.is_used = True
        if commit:
            self.save(update_fields=['is_used'])


def clean_expired_tokens():
    """
    Clean up used and expired tokens.
    """
    threshold = datetime.now(timezone.utc) - timedelta(seconds=600)
    expired = PasswordResetToken.objects.filter(created__lte=threshold)
    used = PasswordResetToken.objects.filter(is_used=True)
    (used | expired).delete()
