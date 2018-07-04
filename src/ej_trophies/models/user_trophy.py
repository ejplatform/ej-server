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
        blank=True,
        default=0,
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
        return UserTrophy.objects.filter(
            trophy__is_active=True,
            user=user
        )

    def get_user_trophy(user, trophy_key):
        """
        Return user's trophy specified by key
        """
        return UserTrophy.objects.filter(
            trophy__is_active=True,
            user=user,
            trophy__key=trophy_key
        )

    def sync_available_trophies_with_user(user):
        """
        Create User association with available trophies
        """
        available_trophies = Trophy.objects.filter(
            is_active=True
        ).exclude(
            users=user
        )

        for trophy in available_trophies:
            UserTrophy.objects.create(
                user=user,
                trophy=trophy
            )

    class Meta:
        verbose_name = _('user\'s trophy')
        verbose_name_plural = _('user\'s trophies')
