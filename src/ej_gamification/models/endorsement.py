import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeFramedModel

NO_PROMOTE_MSG = _('user does not have the right to promote this comment')
log = logging.getLogger('ej')


class Endorsement(TimeFramedModel):
    """
    User endorsement to an specific comment.

    Use :func:`ej_gamification.promote_comment` instead of creating instances
    of this class manually.
    """
    comment = models.ForeignKey(
        'ej_conversations.Comment',
        on_delete=models.CASCADE,
        related_name='endorsements',
    )
    endorser = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='given_endorsements',
    )
    affected_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='affecting_endorsements',
    )
    is_global = models.BooleanField(
        _('Is it global?'),
        default=False,
        help_text=_(
            'Global comments affect all users in conversation'
        ),
    )
    is_expired = property(lambda self: self.end < datetime.now(timezone.utc))

    def recycle(self):
        """
        Remove itself from database if promotion is expired.
        """
        if self.is_expired:
            self.delete()
            self.id = None
            log.info(f'Removed expired promotion for {self.comment} comment.')
        return self
