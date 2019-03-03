from sidekick import import_later
from sklearn.preprocessing import Imputer

from ej_clusters.math.kmeans import euclidean_distance as distance

np = import_later('numpy')


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
