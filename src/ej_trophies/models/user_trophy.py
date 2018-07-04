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
        on_delete=models.CASCADE
    )

    trophy = models.ForeignKey(
        Trophy,
        on_delete=models.CASCADE
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

    class Meta:
        verbose_name_plural = _('user trophies')
