from django.utils.translation import ugettext_lazy as _
from sidekick import alias

from boogie import models
from boogie.fields import EnumField
from boogie.models import QuerySet
from ej_conversations import Choice
from ej_conversations.models import VoteQuerySet, CommentQuerySet


# ==============================================================================
# QUERYSET

class StereotypeVoteQuerySet(QuerySet):
    """
    Represents a table of StereotypeVote objects.
    """

    votes = (lambda self: self)
    votes_table = VoteQuerySet.votes_table


# ==============================================================================
# MODEL

class StereotypeVote(models.Model):
    """
    Similar to vote, but it is not associated with a comment.

    It forms a m2m relationship between Stereotypes and comments.
    """
    author = models.ForeignKey(
        'Stereotype',
        related_name='votes',
        on_delete=models.CASCADE,
    )
    comment = models.ForeignKey(
        'ej_conversations.Comment',
        verbose_name=_('Comment'),
        related_name='stereotype_votes',
        on_delete=models.CASCADE,
    )
    choice = EnumField(Choice, _('Choice'))
    stereotype = alias('author')
    objects = StereotypeVoteQuerySet.as_manager()

    def __str__(self):
        return f'StereotypeVote({self.author}, value={self.choice})'


# ==============================================================================
# PATCH STANDARD COMMENT QUERYSET

class CommentQuerySetMixin:
    def stereotype_votes(self):
        """
        Return a queryset with all stereotype votes related to the current
        comments.
        """
        return StereotypeVote.objects.filter(comment__in=self)


CommentQuerySet.stereotype_votes = CommentQuerySetMixin.stereotype_votes
