from collections import Iterable

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

from boogie import db
from boogie.models import QuerySet
from .math import user_statistics

db = db.ej_conversations


class ConversationMixin:
    """
    Implements an interface with a predictable route to fetch conversations,
    comments and votes related to the current queryset.

    Different models may interpret this relation slightly different, and this
    mixin just implements sane defaults.
    """

    def _votes_from_comments(self, comments):
        return comments.votes()

    def conversations(self):
        """
        Return queryset with all conversations associated with the current
        queryset.
        """
        raise NotImplementedError('must be overridden in subclass')

    def comments(self, conversation=None):
        """
        Return queryset with all comments associated with the current
        queryset.
        """
        conversations = self.conversations()
        qs = db.comments.filter(conversation__in=conversations)
        if conversation:
            qs = qs.filter(**conversation_filter(conversation, qs))
        return qs

    def votes(self, conversation=None, comments=None):
        """
        Return a queryset all all votes from the given authors.

        Args:
            conversation:
                Filter comments by conversation, if given. Can be a conversation
                instance, an id, or a queryset.
            comments:
                An optional queryset of comments to filter the return set of
                votes. If given as queryset, ignore the conversation parameter.
        """
        if comments is None:
            comments = self.comments(conversation)
        elif not isinstance(comments, QuerySet):
            comments = self.comments(conversation).filter(comments__in=comments)
        return self._votes_from_comments(comments)

    def votes_table(self, data_imputation=None, conversation=None, comments=None):
        """
        An alias to self.votes().table(), accepts parameters of both functions.
        """
        return self.votes(conversation, comments).votes_table(data_imputation)


class UserMixin(ConversationMixin):
    extend_dataframe = QuerySet.extend_dataframe

    def comments(self, conversation=None):
        """
        Return a comments queryset with all comments voted by the given
        users.

        Args:
            conversation:
                Filter comments by conversation, if given. Can be a conversation
                instance, an id, or a queryset.
        """
        votes = db.vote_objects.filter(author__in=self)
        comments = db.comments.filter(votes__in=votes)
        if conversation:
            comments = comments.filter(**conversation_filter(conversation))
        return comments

    def statistics_summary_dataframe(self, normalization=1.0, votes=None, comments=None):
        """
        Return a dataframe with basic voting statistics.

        The resulting dataframe has the 'author', 'text', 'agree', 'disagree'
        'skipped', 'divergence' and 'participation' columns.
        """

        if votes is None and comments is None:
            votes = db.votes.filter(author__in=self)
        if votes is None:
            votes = comments.votes().filter(author__in=self)

        votes = votes.dataframe('comment', 'author', 'choice')
        stats = user_statistics(votes, participation=True, divergence=True, ratios=True)
        stats *= normalization
        stats = self.extend_dataframe(stats, 'name', 'email')
        cols = ['name', 'email', 'agree', 'disagree', 'skipped', 'divergence', 'participation']
        return stats[cols]


#
# Auxiliary functions
#
def conversation_filter(conversation, field='conversation'):
    if isinstance(conversation, int):
        return {field + '_id': conversation}
    elif isinstance(conversation, db.conversation_model):
        return {field: conversation}
    elif isinstance(conversation, (QuerySet, Iterable)):
        return {field + '__in': conversation}
    else:
        raise ValueError(f'invalid value for conversation: {conversation}')


#
# Patch user class
#
qs_type = type(get_user_model().objects.get_queryset())
manager_type = type(get_user_model().objects)
if qs_type in (QuerySet, *QuerySet.__bases__):
    raise ImproperlyConfigured(
        'You cannot use a generic QuerySet for your user model.\n'
        'ej_conversations have to patch the queryset class for this model and\n'
        'by adding a new base class and we do not want to patch the base\n'
        'QuerySet since that would affect all models.'
    )
qs_type.__bases__ = (UserMixin, *qs_type.__bases__)
manager_type.__bases__ = (UserMixin, *manager_type.__bases__)
del qs_type, manager_type
