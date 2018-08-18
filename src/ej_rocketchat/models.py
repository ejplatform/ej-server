from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _


class RocketchatSubscription(models.Model):
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
        verbose_name = _('Rocketchat subscription')
        verbose_name_plural = _('Rocketchat subscriptions')
