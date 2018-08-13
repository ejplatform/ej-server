import functools

import numpy as np


def missing_votes(data):
    """
    Return a list of (user, comment) pairs for all missing votes.

    Data
    """
    isna = np.array(data.isna())
    i, j = np.where(isna)
    i = data.index[i]
    j = data.columns[j]
    return np.array(list(zip(i, j)))


def cached(func):
    """
    Cache result of method in the _cache attribute of instance.
    """

    attribute = func.__name__

    @functools.wraps(func)
    def decorated(self, **kwargs):
        key = (attribute, *kwargs.items())
        try:
            return self._cache[key]
        except KeyError:
            self._cache[key] = result = func(self, **kwargs)
            return result

    return decorated


def unpivot(data, users=None, comments=None):
    """
    Convert a 2D pivot table of votes in (user, comments) dimensions to a linear
    data structure of of (user, comment, choice) values representing each
    vote.

    In the absence of missing data, this transforms a table of user x comments
    entries into a table of the same number of votes (thus triplicating the
    table size). Usually we can expect highly sparse data making the unpivoted
    representation more efficient than the pivoted one.
    """
    not_null = np.isfinite
    n_users, n_comments = data.shape
    users = users or range(1, n_users + 1)
    comments = comments or range(1, n_comments + 1)
    return np.array([
        (user, comment, choice)
        for user, row in zip(users, data)
        for comment, choice in zip(comments, row)
        if not_null(choice)
    ])
