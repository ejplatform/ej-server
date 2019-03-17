import logging
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from model_utils.models import TimeFramedModel
from polymorphic.models import PolymorphicModel

from .given_powers_queryset import GivenPowerQuerySet
from ..functions import promote_comment

log = logging.getLogger('ej')


class GivenPower(PolymorphicModel, TimeFramedModel):
    """
    Concede a power to some specific user.

    This object is stored while power is still not in effect.

    Relation with other users are stored in a JSONField to make DB usage more
    efficient.
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='given_powers',
    )
    conversation = models.ForeignKey(
        'ej_conversations.Conversation',
        on_delete=models.CASCADE,
        related_name='given_powers',
    )
    data = JSONField(default=dict)
    is_exhausted = models.BooleanField(default=False)
    is_expired = property(lambda self: self.end < datetime.now(timezone.utc))
    is_active = property(lambda self: not (self.is_expired or self.is_exhausted))
    objects = GivenPowerQuerySet.as_manager()

    @property
    def affected_users(self):
        """
        Queryset with all affected users.
        """
        user_ids = self.data['affected_users']
        return get_user_model().objects.filter(id__in=user_ids)

    @affected_users.setter
    def affected_users(self, users):
        if isinstance(users, QuerySet):
            id_list = list(users.distinct().values_list('id', flat=True))
        else:
            id_list = list(set(user.id for user in users))
        self.data['affected_users'] = id_list

    def use_power(self, **kwargs):
        raise NotImplementedError('implement in subclass')


class GivenBridgePower(GivenPower):
    """
    Given "Conversation bridge" power.
    """

    class Meta:
        proxy = True

    def use_power(self, comment):
        if comment.conversation == self.conversation and not self.is_expired:
            return promote_comment(comment,
                                   author=self.user,
                                   users=self.affected_users.all(),
                                   expires=self.end)
        else:
            raise ValidationError(_('Comment is not in conversation that user can promote or is expired.'))


class GivenMinorityPower(GivenPower):
    """
    Given "Minority activist" power.
    """

    use_power = GivenBridgePower.use_power

    class Meta:
        proxy = True