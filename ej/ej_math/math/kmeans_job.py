import numpy as np

from ej.ej_math.math.kmeans import euclidean_distance, compute_labels


class Kmeans:
    """
    A k-means classification job.
    """

    def __init__(self, data, stereotypes, labels=None, centroids=None,
                 users=None, clusters=None, distance=None):
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
