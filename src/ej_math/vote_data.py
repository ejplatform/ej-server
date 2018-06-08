import numpy as np
import pandas as pd
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

    n_users = lazy(lambda self: len(self.votes['user'].unique()))
    n_comments = lazy(lambda self: len(self.votes['comment'].unique()))
    shape = property(lambda self: self.votes.shape)

    def __init__(self, votes, stereotypes=None):
        keys = votes.keys()
        if not ('user' in keys and 'comment' in keys and 'choice' in keys):
            msg = (f'must be a dataframe with "user", "comment" and "choice" '
                   f'columns, got: {list(keys)}')
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

    def comments(self, field=None, **kwargs):
        """
        Create new dataframe with information about comments.
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
        import surprise

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
        data = pd.DataFrame(votes, columns=['user', 'comment', 'choice'])
    return Math(data)


#
# Compute statistics
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
    pivot = votes.pivot_table('choice', index=which, aggfunc=aggfunc, **kwargs)
    return pivot['choice']


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
