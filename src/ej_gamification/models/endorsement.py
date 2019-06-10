import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, ugettext as __
from model_utils.models import TimeFramedModel

from ..rules import power_expiration_time
from .endorsement_queryset import EndorsementQuerySet

NO_PROMOTE_MSG = _("user does not have the right to promote this comment")
log = logging.getLogger("ej")


class Endorsement(TimeFramedModel):
    """
    User endorsement to an specific comment.

    Endorsements are not necessarily global. Some endorsement might affect only
    a few specific users, depending on the conditions that created the
    endorsement and the clusterization status at the time of the endorsement.

    Use utility functions at ej_gamification instead of creating instances
    of this class manually.
    """

    comment = models.ForeignKey(
        "ej_conversations.Comment",
        on_delete=models.CASCADE,
        related_name="endorsements",
    )
    author = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="given_endorsements"
    )
    affected_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="affecting_endorsements"
    )
    message = models.TextField(
        _("Endorsement reason"),
        blank=True,
        help_text=_(
            "Optional message explaining why the endorsement affected the "
            "given set of users."
        ),
    )
    is_global = models.BooleanField(
        _("Is it global?"),
        default=False,
        help_text=_("Global comments affect all users in conversation"),
    )
    is_expired = property(lambda self: self.end < datetime.now(timezone.utc))
    objects = EndorsementQuerySet.as_manager()

    def __str__(self):
        msg = str(self.comment)
        states = []
        if self.is_global:
            states.append(__("global"))
        if self.is_expired:
            states.append(__("expired"))
        if states:
            states = ", ".join(states)
            msg = f"{msg} ({states})"
        return msg

    def recycle(self):
        """
        Remove itself from database if promotion is expired.
        """
        if self.is_expired:
            self.delete()
            self.id = None
            log.info(f"Removed expired promotion for {self.comment} comment.")
        return self


#
# Special querysets
#
endorsements = Endorsement.timeframed


def endorse_comment(comment, *, author, users=None, expires="default"):
    """
    Promotes comment for the given users.

    Args:
        comment (Comment):
            Promoted comment.
        author (User):
            Author of the endorsement.
        users (sequence of users):
            Queryset or sequence of all users that should see the endorsement.
            Leave blank for global endorsements.
        expires (Datetime):
            Optional date in which the endorsement expires. Can be None, for
            endorsements that never expire, 'default' for comments that expires
            in the default time frame or, finally, an specific datetime.

    Returns:
        A CommentPromotion object
    """
    if expires == "default":
        expires = power_expiration_time("")
    promotion = Endorsement.objects.create(
        comment=comment, author=author, end=expires, is_global=users is None
    )
    if users:
        promotion.affected_users.set(users)
    return promotion


def is_endorsed(comment, user):
    """
    Return True if user sees comment as endorsed.
    """

    return bool(Endorsement.objects.filter(comment=comment, users__id=user.id))


def clean_expired_endorsements():
    """
    Clean all expired endorsements.
    """
    qs = endorsements.filter(end__lte=timezone.now())
    size = qs.count()
    if size > 0:
        qs.delete()
        log.info(f"excluded {size} expired promotions")
