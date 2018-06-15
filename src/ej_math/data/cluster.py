import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_mutual_info_score, adjusted_rand_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Imputer

from .util import missing_votes
from .vote_stats import VoteStats
from ..data_analysis import cluster_error


class ClusterStats(VoteStats):
    def __init__(self, votes, stereotypes=None, user_labels=None, comment_labels=None, **kwargs):
        super().__init__(votes, **kwargs)
        self.stereotypes = stereotypes
        self.user_labels = user_labels
        self.comment_labels = comment_labels

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
