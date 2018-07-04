from .trophy import Trophy
from django.core.validators import MaxValueValidator
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from boogie.rest import rest_api

User = get_user_model()

@rest_api(base_name='users-trophies', base_url='users-trophies')
class UserTrophy(models.Model):
    """
    Intermediary Model with related data between Users and Trophies
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('user')
    )

    trophy = models.ForeignKey(
        Trophy,
        on_delete=models.CASCADE,
        verbose_name=_('trophy')
    )

    percentage = models.PositiveIntegerField(
        _('percentage of progress'),
        validators=[MaxValueValidator(100)]
    )

    # TODO: Remove it after notification module is available
    notified = models.BooleanField(
        _('notified?'),
        blank=True,
        default=False,
        help_text=_('temporary field to track if the user saw the notification or not')
    )

    def get_user_trophies(user):
        """
        Return all user's trophies
        """
        return UserTrophy.objects.filter(user=user)

    def get_user_trophy(user, trophy_key):
        """
        Return user's trophy specified by key
        """
        return UserTrophy.objects.filter(user=user,trophy__key=trophy_key)

    class Meta:
        verbose_name = _('user\'s trophy')
        verbose_name_plural = _('user\'s trophies')
