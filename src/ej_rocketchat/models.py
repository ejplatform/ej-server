from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _


class RocketChatSubscription(models.Model):
    """
    Register subscription of a EJ user into rocket
    """

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='rocketchat_subscriptions',
    )
    is_active = models.BooleanField(
        _('Active?'),
        default=True,
    )

    class Meta:
        permissions = [
            ('can_access_rocketchat', _('Subscribe to rocket chat.')),
        ]
