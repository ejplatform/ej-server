import logging

from boogie import models, db
from .vote import Vote
from ..math import comment_statistics
from ..mixins import ConversationMixin

log = logging.getLogger('ej')


class CommentQuerySet(ConversationMixin, models.QuerySet):
    """
    A table of comments.
    """
    comments = (lambda self, conversation=None: self)

    def _votes_from_comments(self, comments):
        return Vote.objects.filter(comment__in=self)

    def conversations(self):
        conversations = self.values_list('conversation', flat=True)
        return db.ej_conversations.conversations.filter(id__in=conversations)

    def approved(self):
        """
        Keeps only approved comments.
        """
        return self.filter(status=self.model.STATUS.approved)

    def pending(self):
        """
        Keeps only pending comments.
        """
        return self.filter(status=self.model.STATUS.pending)

    def rejected(self):
        """
        Keeps only rejected comments.
        """
        return self.filter(status=self.model.STATUS.rejected)

    def statistics(self):
        return [x.statistics() for x in self]

    def statistics_summary_dataframe(self, normalization=1.0, votes=None):
        """
        Return a dataframe with basic voting statistics.

        The resulting dataframe has the 'author', 'text', 'agree', 'disagree'
        'skipped', 'divergence' and 'participation' columns.
        """
        votes = (votes or self.votes()).dataframe('comment', 'author', 'choice')
        stats = comment_statistics(votes, participation=True, divergence=True, ratios=True)
        stats *= normalization
        stats = self.extend_dataframe(stats, 'author__name', 'content')
        stats['author'] = stats.pop('author__name')
        cols = ['author', 'content', 'agree', 'disagree', 'skipped', 'divergence', 'participation']
        return stats[cols]
