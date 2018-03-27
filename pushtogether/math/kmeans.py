"""
K-means clustering implementation.

This module has no dependency on EJ and will stay here for a while. Once the API stabilizes, it will be
implemented in Cython and will move to an external package.
"""
import collections
import random

import numpy as np


class Kmeans:
    """
    A k-means classification job.
    """

    def __init__(self, data, stereotypes, labels=None, centroids=None, users=None, clusters=None, distance=None):
        self.data = data
        self.stereotypes = stereotypes
        self.labels = labels
        self.centroids = centroids
        self.users = users
        self.clusters = clusters
        self.distance = distance or euclidean_distance

    def update(self, votes):
        """
        Return an updated copy of classifier.
        """
        # Update data and labels
        votes = np.asarray(votes)
        labels = np.append(self.labels, self.classify(votes))
        data = np.vstack(self.data, votes)
        return Kmeans(data, self.stereotypes, labels)

    def classify(self, votes):
        """
        Classify a sequence of votes with the current state of the classifier.
        """
        cluster_names = self.clusters
        labels = compute_labels(votes, self.centroids, self.distance)
        return np.array([cluster_names[i] for i in labels])


class Store(collections.Mapping):
    """
    A cache that keeps the most recently used objects.
    """

    def __init__(self, function, max_size=256):
        self._data = {}
        self._order = []
        self.function = function
        self.max_size = max_size

    def __missing__(self, key):
        self._data[key] = value = self.function(key)
        return value

    def __getitem__(self, item):
        order = self._order
        try:
            value = self._data[item]
            if item != order[-1]:
                del order[order.index(item)]
                order.append(item)
        except KeyError:
            self._data[item] = value = self.function(item)
            order.append(item)

            while len(order) > self.max_size:
                del self._data[order.pop(0)]
        return value

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def update_item(self, key, function):
        """
        Apply function to item in the given key and update result.
        """
        data = self[key]
        self[key] = function(data)


def kmeans(data, k, nruns=10, **kwargs):
    """
    Run kmeans nruns times and returns the (labels, centroids) for the best result.

    Args:
        data: input data of (samples, features)
        k (int): number of returning clusters
        nruns: number of parallel runs

    Return:
        labels: an 1D array of labels for each data point
        centroids: [k, features] array for each centroid

    See also:
        It accepts all keyword arguments of the :func:`kmeans_single` function.
    """
    distance = kwargs.get('distance')
    objective = (lambda x: vq(data, *x, distance=distance))
    return worker(nruns, objective, kmeans_run, data, k, **kwargs)


def worker(nruns, objective, func, *args, **kwargs):
    """
    Worker function: runs func(*args, **kwargs) nruns times and return the
    result with the largest value for the objective function.
    """
    # Use threads in the future?
    results = [func(*args, **kwargs) for _ in range(nruns)]
    return max(results, key=objective)


def kmeans_stereotypes(data, stereotypes, max_iter=20, distance=None, aggregator=None):
    """
    Implements k-means clustering with defined stereotypes.

    Stereotypes have two roles:

    * They guide the clustering procedure by providing a direction for each cluster
    * They serve as a initial guide that removes the requirement of having multiple parallel runs of the algorithm

    Args:
        data: input data of (samples, features)
        stereotypes: average feature set for each stereotype (k, features)

    Returns:
        Two arrays of (labels, centroids)
    """
    k = len(stereotypes)
    data = np.asarray(data)
    data_ext = np.vstack([data, stereotypes])
    labels_extra = np.arange(k, dtype=int)
    stereotypes = np.asarray(stereotypes)
    centroids = stereotypes.copy()
    labels = np.random.randint(0, k, size=len(data))

    for i in range(max_iter):
        labels_ = compute_labels(data, centroids, distance)
        if (labels_ == labels).all():
            return labels_, centroids
        labels_ext = np.append(labels_, labels_extra)
        centroids = compute_centroids(data_ext, labels_ext, k, aggregator)
        labels = labels_
    return labels, centroids


def kmeans_run(data, k, max_iter=10, init_centroids=None, distance=None, aggregator=None):
    """
    Compute a single k-means run with at most max_iter iterations.

    Args:
        data: The input data of (samples, features)
        k: number of returning clusters
        init_centroids: control centroid initialization (init_kmeanspp)
        distance: distance function (euclidean_distance)
        aggregator: aggregator function that computes clusters from samples (mean_aggregator)

    Returns:
        Two arrays of (labels, centroids)
    """
    init_centroids = init_centroids or init_kmeanspp
    distance = distance or euclidean_distance
    data = np.asarray(data)

    centroids = init_centroids(data, k)
    labels = np.random.randint(0, k, size=len(data))
    for i in range(max_iter):
        labels_ = compute_labels(data, centroids, distance)
        if (labels_ == labels).all():
            return labels_, centroids
        centroids = compute_centroids(data, labels_, k, aggregator)
        labels = labels_
    return labels, centroids


def init_kmeanspp(data, k):
    """
    Uses Kmeans++ strategy for initializing centroids: just pick k random different points.
    """
    N = len(data)

    # Pick indexes
    if k == N:
        selected = range(N)
    elif k > N:
        raise ValueError(f'we need at least {N} samples in the dataset')
    else:
        selected = set()
        while len(selected) < N:
            selected.add(random.randrange(0, N))

    return np.array([data[i] for i in selected])


def compute_labels(data, centroids, distance=None):
    """
    Label each data point to its closest centroid.

    Args:
        data: The input data of (samples, features)
        centroids: Centroids (k, features)
        distance: the distance function (defaults to Euclidean distance)
    """
    data = np.asarray(data)
    centroids = np.asarray(centroids)

    n_samples, n_features = data.shape
    k = len(centroids)
    distance = distance or euclidean_distance
    distances = np.empty([n_samples, k])
    for i, sample in enumerate(data):
        for j, centroid in enumerate(centroids):
            distances[i, j] = distance(sample, centroid)
    return distances.argmin(axis=1)


def compute_centroids(data, labels, k, aggregator=None):
    """
    Compute centroids from data and labels.

    Args:
        data: The input data of (samples, features)
        labels: The label for each sample point (samples)
        aggregator: aggregation function that receives a sub-sample and return the corresponding centroid.
    """
    aggregator = aggregator or mean_aggregator
    labels = np.asarray(labels)
    data = np.asarray(data)

    return np.array([aggregator(data[labels == k_]) for k_ in range(k)])


#
# Distance functions
#
def euclidean_distance(x, y):
    """
    Euclidean distance between two arrays.
    """
    x, y = np.asarray(x), np.asarray(y)
    diff = x - y
    diff *= diff
    return np.sqrt(np.sum(diff))


def euclidean_distance_non_zero(x, y):
    """
    Euclidean distance between two arrays ignoring components that have zeros.

    Squared distance is normalized by the number of non-zero components. The rationale
    is that zero represents missing data and should be ignored from computation.
    """
    x, y = np.asarray(x), np.asarray(y)
    zeros = (x == 0) | (y == 0)
    non_zero = len(x) - zeros.sum()
    diff = np.where(zeros, 0, x - y)
    diff *= diff
    return np.sqrt(np.sum(diff) / non_zero)


def l1_distance(x, y):
    """
    L1 (Manhattan/cab-driver) distance between two arrays.
    """
    return np.sum(np.abs(x - y))


def vq(data, labels, centroids, distance=None):
    """
    Return the variation coefficient of data.
    """
    distance = distance or euclidean_distance
    return sum(
        sum(distance(centroid, sample) ** 2 for sample in data[labels == k])
        for k, centroid in enumerate(centroids)
    )


#
# Aggregation functions
#
def mean_aggregator(data):
    """
    Return the mean value of cluster.
    """
    return data.mean(axis=0)
