from functools import lru_cache

from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from model_utils.models import StatusModel

from boogie.rest import rest_api
from ej_clusters.models import Cluster
from ej_conversations.fields import UserRef, CommentRef, ConversationRef
from ej_conversations.models import Comment
from .functions import promote_comment

NO_PROMOTE_MSG = _('user does not have the right to promote this comment')


@rest_api()
class CommentEndorsement(models.Model):
    """
    Keeps track of who endorse each comment.
    """

    comment = CommentRef()
    user = UserRef()

    class Meta:
        unique_together = [('comment', 'user')]


@rest_api()
class EndorsementRight(StatusModel):
    """
    User can endorse a comment in a conversation.
    """

    STATUS = Choices(
        ('any', _('Any comment in conversation')),
        ('self', _('Self promotion')),
        ('other', _('Endorse comment from other user')),
        ('group', _('Endorse comment from a user in the user\'s cluster')),
        ('other_group', _('Endorse comment from user from a different cluster')),
    )
    user = UserRef()
    conversation = ConversationRef()

    @lru_cache(16)
    def allowed_comments(self):
        """
        Return all comments that can be endorsed by the current right.
        """
        comments = Comment.objects.filter(conversation_id=self.conversation_id)

        if self.status == self.STATUS.any:
            return comments
        elif self.status == self.STATUS.self:
            return comments.filter(author_id=self.user_id)
        elif self.status == self.STATUS.other:
            return comments.exclude(author_id=self.user_id)

        try:
            cluster = Cluster.objects.get(user_id=self.user_id,
                                          conversation_id=self.conversation_id)
        except Cluster.DoesNotExist:
            return comments.empty()
        group = cluster.users.all()

        if self.status == self.STATUS.group:
            return comments.exclude(author__in=group)
        elif self.status == self.STATUS.other_group:
            return comments.exclude(author__in=group)
        else:
            raise ValueError('invalid status: %s' % self.status)

    def promote(self, comment):
        """
        Endorse the given comment. This removes the endorsement right from the
        database.
        """
        if comment not in self.allowed_comments():
            raise PermissionError(NO_PROMOTE_MSG)
        with transaction.atomic():
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
    endorsed_comments = models.PositiveSmallIntegerField()
    endorsement_actions = models.PositiveSmallIntegerField()

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
