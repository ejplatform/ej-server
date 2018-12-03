from random import randrange

import pandas as pd
from django.db.models import Manager
from sidekick import import_later

from boogie.models import QuerySet

models = import_later('.models', package=__package__)


class ConversationQuerySet(QuerySet):
    def random(self, user=None, **kwargs):
        """
        Return a random conversation.

        If user is given, tries to select the conversation that is most likely
        to engage the given user.
        """
        return self._random() if user is None else self._random_for_user(user)

    def _random_for_user(self, user):
        # TODO: implement this!
        return self._random()

    def _random(self):
        size = self.count()
        return self.all()[randrange(size)]


class CommentQuerySet(QuerySet):
    DEFAULT_COLUMNS = {
        'content': 'text',
        'author__name': 'author',
        'conversation__title': 'conversation',
    }

    def approved(self):
        return self.filter(status=self.model.STATUS.approved)

    def pending(self):
        return self.filter(status=self.model.STATUS.pending)

    def rejected(self):
        return self.filter(status=self.model.STATUS.rejected)

    def statistics(self):
        return [x.statistics() for x in self]

    def display_dataframe(self, columns=DEFAULT_COLUMNS):
        qs = self.values_list('id', *columns.keys())
        df = pd.DataFrame(list(qs), columns=['id', *columns.values()])
        df.index = df.pop('id')
        return df

    def votes(self):
        """
        Return a queryset with all votes related to the current comments.
        """
        return models.Vote.objects.filter(comment__in=self)

    def voting_statistics(self):
        votes = self.votes().dataframe('comment', 'author', 'choice')
        n_users = len(votes['author'].unique())
        stats = comment_statistics(votes, pc=True)
        stats['divergence'] = divergence(stats, places=0)
        stats['participation'] = participation(stats, places=0, users=n_users)
        stats = self.extend_dataframe(stats, 'author', 'text')
        return stats[['author', 'text', 'agree', 'disagree', 'skipped',
                      'divergence', 'participation']]


#
# Manager classes
#
ConversationManager = Manager.from_queryset(ConversationQuerySet, 'ConversationManager')
CommentManager = Manager.from_queryset(CommentQuerySet, 'CommentManager')


#
# Utility functions
#
def comment_statistics(votes, author='author', comment='comment',
                       choice='choice', pc=False, places=0):
    """
    Return a dataframe counting the number of votes for each comment/choice
    from an input dataframe of votes.
    """

    group = votes.groupby([comment, choice])
    df = group.count()
    extra = df.index.to_frame()
    df[comment] = extra[comment]
    df[choice] = extra[choice]
    df.index = df.reindex()
    table = df.pivot_table(index=comment, columns=choice, values=author,
                           fill_value=0)

    # Convert values to percentages when requested.
    if pc:
        total = table.sum(axis=1)
        data = 100 * table.values / total.values[:, None]
        table = pd.DataFrame(data, columns=table.columns, index=table.index)
        if places is not None:
            table = table.round(places)

    # Fill empty columns and update their names.
    col_names = {1: 'agree', -1: 'disagree', 0: 'skipped'}
    for col in col_names:
        if col not in table:
            table[col] = 0
    table.columns = [col_names[k] for k in table.columns]

    # Result
    return table


def divergence(df, agree='agree', disagree='disagree', places=None):
    """
    Compute the divergence column from a dataframe that have an 'agree' and a
    'disagree' columns.
    """
    e = 1e-50
    col = abs(df[agree] - df[disagree]) / (df[agree] + df[disagree] + e)
    if places is not None:
        col = col.round(places)
    return col


def participation(df, users,
                  agree='agree', disagree='disagree', skipped='skipped',
                  places=0):
    """
    Compute the participation column from the total number of users and a
    dataframe that have 'agree', 'disagree' and 'skipped' columns.
    """
    e = 1e-50
    col = users / (df[agree] + df[disagree] + df[skipped] + e)
    if places is not None:
        col = col.round(places)
    return col
