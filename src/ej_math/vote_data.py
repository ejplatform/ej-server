import numpy as np
import pandas as pd
import surprise
from lazyutils import lazy
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_mutual_info_score, adjusted_rand_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Imputer

from .data_analysis import cluster_error
from .math.kmeans import euclidean_distance as distance

DISAGREE, SKIP, AGREE = -1, 0, 1


class Math:
    """
    Compute statistics, indexes, and perform generic mathematical analysis
    about votes and comments in a conversation.
    """

    num_users = lazy(lambda self: len(self.votes['user'].unique()))
    shape = property(lambda self: self.votes.shape)

    def __init__(self, votes, stereotypes=None):
        keys = votes.keys()
        if not ('user' in keys and 'comment' in keys and 'vote' in keys):
            msg = 'must be a dataframe with "user", "comment" and "votes" columns'
            raise ValueError(msg)
        self.votes = votes
        self.stereotypes = stereotypes
        self.user_labels = None
        self.comment_labels = None

    @lazy
    def pivot_table(self):
        """
        Dataframe with users as index, comments as columns and votes as
        values.
        """
        votes = self.votes
        return votes.pivot_table(index='user', columns='comment', values='vote')

    # Dataframes with user and comment statistics
    def comments(self, field=None, **kwargs):
        """
        Create new dataframe with information about comments.
        """

        votes = (lambda x, **kwargs: num_votes(x, 'comment', **kwargs))
        average = (lambda x, **kwargs: average_vote(x, 'comment', **kwargs))

        if field is None:
            df = base_stats(self.num_users, votes, average, **kwargs)
            if self.comment_labels is not None:
                df['cluster'] = self.comment_labels
        else:
            raise NotImplementedError

        return df

    def users(self, field=None, **kwargs):
        """
        Return a dataframe with statistics about users.
        """
        votes = (lambda x, **kwargs: num_votes(x, 'user', **kwargs))
        average = (lambda x, **kwargs: average_vote(x, 'user', **kwargs))

        if field is None:
            df = base_stats(self.num_users, votes, average, **kwargs)

        labels = self.user_labels
        if labels is not None:
            df['cluster'] = labels
            df['op_bridge'] = opinion_bridge_index(self.votes, labels)

        return df

    #
    # Clusterization
    #
    def clusters(self, k=None, method='kmeans', ret_clusterizer=False, **kwargs):
        """
        Extract clusters from input data.
        """

        pipeline = Pipeline([
            ('fill', Imputer()),
            ('cluster', KMeans(k or 4, **kwargs))
        ])
        labels = pipeline.fit_predict(self.pivot_table)
        if ret_clusterizer:
            return labels, pipeline
        else:
            return labels

    def compare_labels(self, true_labels, k, method='error-complement'):
        """
        Clusterize and compare labels.
        """
        if self.user_labels is None:
            inferred_labels = self.user_labels
        else:
            inferred_labels, _ = self.clusters(k)

        if method == 'error-complement':
            return 1 - cluster_error(inferred_labels, true_labels)
        elif method == 'mutual-information':
            return adjusted_mutual_info_score(inferred_labels, true_labels)
        elif method == 'ransurprised':
            return adjusted_rand_score(inferred_labels, true_labels)
        else:
            raise ValueError(f'invalid method: {method}')

    # Vote inference and collaborative filtering
    def infer_votes(self, round=False, type='nmf', n_factors=8, **kwargs):
        """
        Return a list of inferred votes for missing data.
        """
        algo_class = {
            'knn': surprise.KNNBasic,
            'knn-means': surprise.KNNWithMeans,
            'knn-baseline': surprise.KNNBaseline,
            'knn-zscore': surprise.KNNWithZScore,
            'nmf': surprise.NMF,
            'svd': surprise.SVD,
            'svd++': surprise.SVDpp,
            'baseline': surprise.BaselineOnly,
        }[type]

        reader = surprise.Reader(rating_scale=(-1, 1))
        data = surprise.Dataset.load_from_df(self.votes, reader)
        train = data.build_full_trainset()

        kwargs.setdefault('verbose', False)
        algo = algo_class(n_factors=n_factors, **kwargs)
        algo.fit(train)

        predictions = []
        for uid, iid in missing_votes(self.pivot_table):
            prediction = algo.predict(uid, iid)
            predictions.append((uid, iid, prediction.est))

        if round:
            np.round(predictions)

        return pd.DataFrame(predictions, columns=['user', 'comment', 'vote'])

    def fill(self, *args, **kwargs):
        """
        Fill missing votes and return a copy.
        """
        votes = self.infer_votes(*args, **kwargs)
        return type(self)(self.votes.append(votes))

    def imputer(self):
        """
        Scikit learn
        """


#
# Load data
#
def read_data(votes, users=None, comments=None, pivot=False):
    """
    Return a new vote statistics object from input data.

    Args:
        votes:
            A queryset, ...
    """
    # If data is in the form of users x comments, we should unpivot it before
    # loading the statistics object
    if pivot:
        votes = unpivot(votes, users, comments)

    if isinstance(votes, pd.DataFrame):
        data = votes
    else:
        votes = np.asarray(votes)
        data = pd.DataFrame(votes, columns=['user', 'comment', 'vote'])
    return Math(data)


#
# Compute statistics
#
def base_stats(num_users, count_func, average_func, advanced=True, pc=False):
    """
    Return a dataframe with all basic statistics about a user.
    """

    df = pd.DataFrame()

    n_votes = count_func()
    n_voted = count_func(drop_skip=True)

    df['votes'] = n_votes
    df['missing'] = 1 - n_votes / num_users
    df['skipped'] = 1 - n_voted / n_votes
    df['agree'] = count_func(drop_skip=True, value=AGREE) / n_voted

    # Advanced statistics
    if advanced:
        df['average'] = average_func()
        df['divergence'] = np.abs(average_func(drop_skip=True))
        df['entropy'] = binary_entropy(df.agree)

    # Display percentages?
    if pc:
        fraction_fields = {
            'missing', 'skipped', 'agree', 'average', 'divergence'
        }
        for field in fraction_fields:
            if field in df:
                df[field] *= 100
        df['entropy'] *= 100 / np.log(2)

    return df


def average_vote(votes, which, drop_skip=False):
    return pivoted_data(votes, which, drop_skip=drop_skip, aggfunc=np.mean).vote


def num_votes(votes, which, drop_skip=False, value=None):
    if value is not None:
        votes = votes[votes.vote == value]
    return pivoted_data(votes, which, drop_skip=drop_skip, aggfunc='count').vote


def pivoted_data(df, which, aggfunc=np.mean, drop_skip=False, **kwargs):
    if drop_skip:
        df = df[df.vote != SKIP]
    return df.pivot_table('vote', index=which, aggfunc=aggfunc, **kwargs)


def pivot_comment(df, *args, **kwargs):
    return pivoted_data(df, 'comment', *args, **kwargs)


def pivot_user(df, *args, **kwargs):
    return pivoted_data(df, 'user', *args, **kwargs)


def binary_entropy(p, e=1e-50):
    """
    Entropy for binary probability.
    """
    P = 1 - p
    return -(p * np.log(p + e) + P * np.log(P + e))


#
# Dataset transformations
#
def unpivot(data, users=None, comments=None):
    """
    Convert a 2D pivot table of votes in (user, comments) dimensions to a linear
    data structure of of (user, comment, vote) values representing each vote.

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
        (user, comment, vote)
        for user, row in zip(users, data)
        for comment, vote in zip(comments, row)
        if not_null(vote)
    ])


def missing_votes(data):
    """
    Return a list of (user, comment) pairs for all missing votes.
    """
    isna = np.array(data.isna())
    i, j = np.where(isna)
    i = data.index[i]
    j = data.columns[j]
    return np.array(list(zip(i, j)))


def opinion_bridge_index(df, labels):
    """
    Compute the opinion bridge index for each user.
    """
    labels = np.asarray(labels)
    label_set = sorted(np.unique(labels))
    k = len(label_set)
    n_samples, _ = df.shape

    data = Imputer().fit_transform(df)
    print(data[labels == k])

    centroids = np.array([np.mean(data[labels == label], 0) for label in label_set])

    distances = np.empty([n_samples, k])
    for i, sample in enumerate(data):
        for j, centroid in enumerate(centroids):
            if label_set[j] == labels[i]:
                distances[i, j] = float('inf')
            else:
                distances[i, j] = distance(sample, centroid)
    return distances.min(axis=1)


def max_opinion_bridge(size, k):
    return int(min(max(1, 0.05 * size)), k)
