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

from ej_gamification.models import endorse_comment
from ej_gamification.rules import power_expiration_time

log = logging.getLogger('ej')


class GivenPower(PolymorphicModel, TimeFramedModel):
    """
    Power conceded to some specific user.

    This object is active while power is still not in effect. When user decides
    to use the power, it sets is_exhausted to True and executes the effects of
    the power.

    A JSONField is used to store non-structured data that may be present in a
    different form to different users or might make db access more efficient
    by replacing the need for M2M fields that might spawn additional queries.
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

    def use_power(self, request, related=None, info=None):
        """
        Use power in (optional) related object.

        The power is updated and saved to the database.

        Args:
            request:
                The current request. Necessary to send feedback messages to
                users.
            related:
                An optional related object that is pertinent to the way the
                power is consumed.
            info:
                An optional dictionary that can contain extra information on
                how the power should be applied.
        """
        self._use_power(request, related, info=info or {})
        self.save()

    def _use_power(self, request, related, info):
        raise NotImplementedError('must be implemented in subclass')


# ------------------------------------------------------------------------------
# Mixin classes
# ------------------------------------------------------------------------------
class HasAffectedUsersMixin:
    """
    Mixin for powers that define a field "affected_users" in its JSON structure
    that contains a list of primary keys to users affected by the power.
    """

    conversation: models.Model
    data: dict
    end: datetime
    is_expired: bool
    user: models.Model

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


class EndorsementPowerMixin(HasAffectedUsersMixin):
    """
    A power that promotes the endorsement of some comment when user uses it.
    """

    def _use_power(self, _request, related, _info):
        comment = related
        if comment.conversation != self.conversation:
            raise ValidationError(_('Comment is not in conversation that user can promote.'))
        elif self.is_expired:
            raise ValidationError(_('Sorry, your power is expired'))
        else:
            return endorse_comment(comment,
                                   author=self.user,
                                   users=self.affected_users.all(),
                                   expires=self.end)


# ------------------------------------------------------------------------------
# Concrete powers
# ------------------------------------------------------------------------------

class GivenBridgePower(EndorsementPowerMixin, GivenPower):
    """
    Given "Conversation bridge" power.
    """

    slug = 'bridge-power'

    class Meta:
        proxy = True


class GivenMinorityPower(EndorsementPowerMixin, GivenPower):
    """
    Given "Minority activist" power.
    """

    slug = 'minority-power'

    class Meta:
        proxy = True


# ------------------------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------------------------

def give_minority_power(user, conversation, users, expires='default'):
    """
    Create Minority power for user to promote comments.

    Args:
        user (User):
            User receiving power
        conversation (Conversation):
            Conversation that for which power will be available.
        users (sequence or queryset):
            List of users affected by this power
        expires:
            Optional expiration datetime

    Returns:
        A GivenMinorityPower object
    """
    return _give_promotion_power(GivenMinorityPower, user, conversation, users, expires)


def give_bridge_power(user, conversation, users, expires='default'):
    """
    Create Bridge power for user to promote comments

    Args:
        user (User):
            User receiving power
        conversation (Conversation):
            Conversation that for which power will be available.
        users (sequence or queryset):
            List of users affected by this power
        expires:
            Optional expiration datetime

    Returns:
        A GivenBridgePower object
    """
    return _give_promotion_power(GivenBridgePower, user, conversation, users, expires)


def _give_promotion_power(power_class, user, conversation, users, expires):
    """
    Used internally by give_minority_power and give_bridge_power.
    """
    expires = expires or power_expiration_time(power_class.slug)
    power = power_class(user=user, conversation=conversation, end=expires)
    power.affected_users = users
    power.save()
    return power


def clean_expired_promotion_powers():
    """
    Mark all expired promotion powers and clean unnecessary information from the
    database.
    """

    qs = GivenPower.objects \
        .filter(end__lte=timezone.now()) \
        .get_real_instances()

    size = len(qs.update(is_expired=True, data={}))
    log.info(f'excluded {size} expired promotion powers')
