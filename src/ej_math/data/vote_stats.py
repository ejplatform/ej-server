import numpy as np
import pandas as pd
from lazyutils import lazy

DISAGREE, SKIP, AGREE = -1, 0, 1


class VoteStats:
    """
    Compute statistics, indexes, and perform generic mathematical analysis
    about votes and comments in a conversation.
    """

    n_users = lazy(lambda self: len(self.votes['user'].unique()))
    n_comments = lazy(lambda self: len(self.votes['comment'].unique()))
    shape = property(lambda self: self.votes.shape)

    def __init__(self, votes, n_users=None, n_comments=None):
        if not isinstance(votes, pd.DataFrame):
            votes = list(votes)
            votes = pd.DataFrame(votes, columns=['user', 'comment', 'choice'])

        keys = votes.keys()
        if not ('user' in keys and 'comment' in keys and 'choice' in keys):
            msg = (f'must be a dataframe with "user", "comment" and "choice" '
                   f'columns, got: {list(keys)}')
            raise ValueError(msg)
        self.votes = votes
        if n_users is not None:
            self.n_users = n_users
        if n_comments is not None:
            self.n_comments = n_comments

    @lazy
    def pivot_table(self):
        """
        Dataframe with users as index, comments as columns and votes as
        values.
        """
        votes = self.votes
        return votes.pivot_table(index='user', columns='comment', values='choice')

    # Dataframes with user and comment statistics
    def _datasets(self, which, n_max):
        data = self.votes
        return dict(
            n_votes=num_votes(data, which),
            n_skip=num_votes(data, which, choice=SKIP),
            n_agree=num_votes(data, which, choice=AGREE),
            n_disagree=num_votes(data, which, choice=DISAGREE),
            n_max=n_max,
            avg_all=average_vote(data, which),
            avg_valid=average_vote(data, which, drop_skip=True),
        )

    def comments(self, **kwargs):
        """
        Return a dataframe with information about comments.
        """
        kwargs = dict(self._datasets('comment', self.n_users), **kwargs)
        return base_stats(**kwargs)

    def users(self, **kwargs):
        """
        Return a dataframe with statistics about users.
        """
        data = self._datasets('user', self.n_comments)
        kwargs = dict(data, **kwargs)
        return base_stats(**kwargs)


#
# Auxilixary functions
#
def base_stats(n_votes, n_agree, n_disagree, n_skip, n_max,
               advanced=True, pc=False,
               avg_all=None, avg_valid=None,
               **kwargs):
    """
    Return a dataframe with basic statistics.

    Args:
        n_votes (array):
            Number of votes for each entry.
        n_skip/n_agree/n_disagree (array):
            Number of votes for each choice.
        n_max(int):
            Total number of elements in sample.
        advanced (bool):
            If true, show advanced statistics (average vote counts)
        pc (bool):
            If true, return all statistics as percentages (when applicable).
        avg_all/avg_valid (array):
            Average vote value for each entry. The first include all votes and
            the second ignores the skipped votes.
    """
    e = 1e-50
    df = pd.DataFrame()
    n = pd.DataFrame({
        'total': n_votes,
        'agree': n_agree, 'disagree': n_disagree, 'skip': n_skip,
    }).fillna(0).astype(int)

    df['votes'] = n.total
    df['missing'] = (n_max - n.total) / n_max
    df['skipped'] = n.skip / (n.total + e)
    df['agree'] = n.agree / (n.total - n.skip + e)
    df['disagree'] = n.disagree / (n.total - n.skip + e)

    # Advanced statistics
    if advanced:
        if avg_all is None or avg_valid is None:
            msg = 'avg_all and avg_valid must be given for advanced statistics'
            raise TypeError(msg)
        df['average'] = avg_all
        df['divergence'] = np.abs(avg_valid)
        df['entropy'] = binary_entropy(df.agree)

    # Extra columns
    if kwargs:
        df.update(kwargs)

    # Display percentages?
    if pc:
        fraction_fields = {
            'missing', 'skipped', 'agree', 'disagree', 'average', 'divergence'
        }
        for field in fraction_fields:
            if field in df:
                df[field] *= 100
        df['entropy'] *= 100 / np.log(2)

    return df


def average_vote(votes, which, drop_skip=False):
    return pivoted_data(votes, which, drop_skip=drop_skip, aggfunc=np.mean)


def num_votes(votes, which, drop_skip=False, choice=None):
    if choice is not None:
        votes = votes[votes['choice'] == choice]
    return pivoted_data(votes, which, drop_skip=drop_skip, aggfunc='count')


def pivoted_data(votes, which, aggfunc=np.mean, drop_skip=False, **kwargs):
    if drop_skip:
        votes = votes[votes['choice'] != SKIP]

    if len(votes) == 0:
        return pd.Series([])
    pivot = votes.pivot_table('choice', index=which, aggfunc=aggfunc, **kwargs)
    return pivot['choice']


def binary_entropy(p, e=1e-50):
    """
    Entropy for binary probability.
    """
    P = 1 - p
    return -(p * np.log(p + e) + P * np.log(P + e))
