import logging
from datetime import datetime
from django.utils import timezone
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from model_utils.models import TimeFramedModel
from polymorphic.models import PolymorphicModel
from picklefield.fields import PickledObjectField

from ej_conversations.fields import UserRef, CommentRef, ConversationRef
from .functions import promote_comment

NO_PROMOTE_MSG = _('user does not have the right to promote this comment')
log = logging.getLogger('ej')


class CommentPromotion(TimeFramedModel):
    """
    Describes the act of one user promoting an specific comment.

    Better use the :func:`ej_powers.promote_comment` function instead of
    creating instances of this class manually.
    """
    comment = CommentRef()
    promoter = UserRef(related_name='promotions')
    users = models.ManyToManyField(
        get_user_model(),
        related_name='see_promotions',
    )
    is_expired = property(lambda self: self.end < datetime.now(timezone.utc))

    def recycle(self):
        """
        Remove itself from database if promotion is expired.
        """
        if self.is_expired:
            self.delete()
            log.info(f'Removed expired promotion for {self.comment} comment.')


class GivenPower(TimeFramedModel, PolymorphicModel):
    """
    Concede a power to some specific user.

    This object is stored while power is still not in effect.

    Relation with other users are stored in a CommaSeparatedIntegerField blob
    to make DB usage more efficient.
    """
    user = UserRef()
    conversation = ConversationRef()
    data = PickledObjectField()
    is_exhausted = models.BooleanField(default=False)
    is_expired = property(lambda self: self.end < datetime.now(timezone.utc))

    def use_power(self, **kwargs):
        raise NotImplementedError('implement in subclass')


class GivenBridgePower(GivenPower):
    """
    Given "Conversation bridge" power.
    """

    class Meta:
        proxy = True

    def get_affected_users(self):
        """
        Return queryset with all affected users.
        """
        user_ids = self.data['affected_users']
        return get_user_model().objects.filter(id__in=user_ids)

    def set_affected_users(self, users):
        """
        Convert users queryset to a list and save it to affected_users
        """
        self.data = {'affected_users': set(user.id for user in users)}

    def use_power(self, comment):
        if comment.conversation == self.conversation and not self.is_expired:
            return promote_comment(comment,
                                   author=self.user,
                                   users=self.get_affected_users(),
                                   expires=self.end)
        else:
            raise ValidationError(_('Comment is not in conversation that user can promote or is expired.'))


class GivenMinorityPower(GivenPower):
    """
    Given "Minority activist" power.
    """

    class Meta:
        proxy = True

    get_affected_users = GivenBridgePower.get_affected_users
    set_affected_users = GivenBridgePower.set_affected_users
    use_power = GivenBridgePower.use_power
