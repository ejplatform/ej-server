from functools import lru_cache

from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from model_utils.models import StatusModel

from ej.ej_math.models import UserRef, CommentRef, ConversationRef

NO_PROMOTE_MSG = _('user does not have the right to promote this comment')


class CommentPromotion(models.Model):
    """
    Keeps track of who promoted each comment.
    """

    comment = CommentRef()
    user = UserRef()

    class Meta:
        unique_together = [('comment', 'user')]


class PromotionRight(StatusModel):
    """
    User can promote a comment in a conversation.
    """

    STATUS = Choices(
        ('self', _('Self promotion')),
        ('other', _('Promote comment from other user')),
        ('group', _('Promote comment from a user in the user\'s cluster')),
        ('other_group', _('Promote comment from user from a different cluster')),
    )
    user = UserRef()
    conversation = ConversationRef()

    @lru_cache(16)
    def allowed_comments(self):
        """
        Return all comments that can be promoted by the current promotion right.
        """
        raise NotImplementedError

    def promote(self, comment):
        """
        Execute promotion right in the given comment.
        """
        if comment not in self.allowed_comments():
            raise PermissionError(NO_PROMOTE_MSG)
        promote_comment(comment, self.user)
        self.delete()


class ConversationPowers(models.Model):
    """
    Register all permanent powers a user can perform in a conversation.
    """

    user = UserRef()
    conversation = ConversationRef()

    # Statistics
    extra_comments = models.PositiveSmallIntegerField()
    promoted_comments = models.PositiveSmallIntegerField()
    promote_actions = models.PositiveSmallIntegerField()

    # Powers
    can_be_clusterized = models.BooleanField(default=False)
    can_see_cluster_names = models.BooleanField(default=False)
    can_see_divergence_distribution = models.BooleanField(default=False)
    can_see_vote_predictions = models.BooleanField(default=False)

    # Achievements
    has_created_comment = models.BooleanField(default=False)
    has_voted_all_comments = models.BooleanField(default=False)
    has_extra_comments = property(lambda self: self.extra_comments > 0)
    has_been_promoted = property(lambda self: self.promoted_comments > 0)
    has_promoted_others = property(lambda self: self.promote_actions > 0)

    # Introspection
    @property
    def has_powers(self):
        return any(getattr(self, attr) for attr in self._boolean_powers
                   if attr != 'has_powers')

    _boolean_powers = [
        x for x in locals()
        if x.startswith('has_') or x.startswith('can_') or x.startswith('is_')
    ]

    class Meta:
        unique_together = [('user', 'conversation')]


powers = ConversationPowers.objects


class ConversationPowersQuerySet(models.QuerySet):
    def incr_by(self, user, conversation, **kwargs):
        """
        Increment the given numeric powers/achievements by the given quantity.
        """
        self.get_powers(user, conversation)

    # TODO
    def incr_all_by(self, **kwargs):
        """
        Increment all values in the current queryset by the given amount.
        """
        raise NotImplementedError

    def get_powers(self, user, conversation):
        """
        Return the ConversationPower instance for user in conversation
        """
        return self.get_or_create(user=user, conversation=conversation)[0]

    def has_powers(self, user, conversation):
        """
        Return True if user has any powers in the given conversation.
        """
        try:
            powers = self.get(user=user, conversation=conversation)
        except ConversationPowers.DoesNotExist:
            return False
        else:
            return powers.has_powers


def promote_comment(comment, user=None):
    """
    Promotes comment.

    If user is given, register that the given user contributed with the
    comment promotion.
    """
    conversation = comment.conversation
    if user:
        powers.incr_by(user, conversation, promote_actions=1)
    if comment.author != user:
        powers.incr_by(comment.author, conversation, promoted_comments=1)
    if not comment.is_promoted:
        comment.is_promoted = True
        comment.save(update_fields=['is_promoted'])
    CommentPromotion.objects.get_or_create(user=user, comment=comment)
