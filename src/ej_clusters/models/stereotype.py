from random import randrange

from django.conf import settings
from django.db.models import OuterRef, Subquery
from django.utils.translation import ugettext_lazy as _

from boogie import models
from boogie.models import QuerySet
from boogie.rest import rest_api
from ej_conversations.enums import Choice
from ej_conversations.mixins import UserMixin, conversation_filter
from ej_conversations.models import Comment
from .stereotype_vote import StereotypeVote
from .. import log


# ==============================================================================
# QUERYSET

class StereotypeQuerySet(UserMixin, QuerySet):
    """
    Represents a table of Stereotype objects.
    """

    _votes_from_comments = (lambda _, comments: comments.stereotype_votes())

    def fill_votes(self, choice=Choice.DISAGREE, comments=None):
        """
        Gather all comments voted by the current queryset and fill the votes of
        the other stereotypes with the given vote.

        Args:
            choice:
                The choice to fill in (agree, disagree, etc)
            comments:
                Optionally restrict votes to the comments in the given
                queryset, if given.

        Returns:
            None
        """
        raise NotImplementedError

    def comments(self, conversation=None):
        """
        Return a comments queryset with all comments voted by the given
        stereotypes.

        Args:
            conversation:
                Filter comments by conversation, if given. Can be a conversation
                instance, an id, or a queryset.
        """
        votes = StereotypeVote.objects.filter(author__in=self)
        comments = Comment.objects.filter(stereotype_votes__in=votes)
        if conversation:
            comments = comments.filter(**conversation_filter(conversation))
        return comments


# ==============================================================================
# MODEL

@rest_api(['name', 'description', 'owner'], inline=True)
class Stereotype(models.Model):
    """
    A "fake" user created to help with classification.
    """

    name = models.CharField(
        _('Name'),
        max_length=64,
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(
        _('Description'),
        blank=True,
        help_text=_(
            'A detailed description of your stereotype for future reference. '
            'You can specify a background history, or give hints on the exact '
            'profile the stereotype wants to capture.'
        ),
    )
    objects = StereotypeQuerySet.as_manager()

    class Meta:
        unique_together = [('name', 'owner')]

    __str__ = (lambda self: self.name)

    def vote(self, comment, choice, commit=True):
        """
        Cast a single vote for the stereotype.
        """
        choice = Choice.normalize(choice)
        log.debug(f'Vote: {self.name} (stereotype) - {choice}')
        vote = StereotypeVote(author=self, comment=comment, choice=choice)
        vote.full_clean()
        if commit:
            vote.save()
        return vote

    def cast_votes(self, choices):
        """
        Create votes from dictionary of comments to choices.
        """
        votes = []
        for comment, choice in choices.items():
            votes.append(self.vote(comment, choice, commit=False))
        StereotypeVote.objects.bulk_update(votes)
        return votes

    def next_comment(self, conversation):
        """
        Get next available comment for the given conversation.
        """
        remaining = self.non_voted_comments(conversation)
        size = remaining.count()
        return remaining[randrange(size)]

    def non_voted_comments(self, conversation):
        """
        Return a queryset with all comments that did not receive votes.
        """
        voted = StereotypeVote.objects.filter(author=self, comment__conversation=conversation)
        comment_ids = voted.values_list('comment', flat=True)
        return conversation.comments.exclude(id__in=comment_ids)

    def voted_comments(self, conversation):
        """
        Return a queryset with all comments that the stereotype has cast votes.

        The resulting queryset is annotated with the vote value using the choice
        attribute.
        """
        voted = StereotypeVote.objects.filter(author=self, comment__conversation=conversation)
        voted_subquery = \
            (voted
                .filter(comment=OuterRef('id'))
                .values('choice'))
        comment_ids = voted.values_list('comment', flat=True)
        return \
            (conversation.comments
                .filter(id__in=comment_ids)
                .annotate(choice=Subquery(voted_subquery)))
