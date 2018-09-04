import logging
from collections import defaultdict

import numpy as np
import pandas as pd

from ej_clusters import math
from .math.kmeans import kmeans_stereotypes, euclidean_distance_finite

update_clusters_original = math.update_clusters

log = logging.getLogger('ej')


def patch():
    math.update_clusters = update_clusters


def update_clusters(conversation, clusters, users=None):
    """
    Assign users to their respective clusters in conversation.
    """

    # Create a dataframe with stereotype votes. The final dataframe has
    # user, comment and vote columns
    stereotype_data = []
    for cluster in clusters:
        df = cluster.mean_stereotype()
        df['comment'] = df.index
        df['user'] = cluster.id
        data = df[['user', 'comment', 'choice']].values
        stereotype_data.append(data)

    data = np.vstack(stereotype_data)
    stereotype_votes = pd.DataFrame(data, columns=['user', 'comment', 'choice'])
    for col in ['user', 'comment']:
        stereotype_votes[col] = stereotype_votes[col].astype(int)

    # Get votes and transform vote data to pivot tables
    votes = math.get_votes(conversation)
    stereotype_votes = math.build_dataframe(stereotype_votes)
    same_columns(votes, stereotype_votes)

    # Use k-means to clusterize data
    labels, _centroids = kmeans_stereotypes(
        votes.values,
        stereotype_votes.values,
        distance=euclidean_distance_finite,
    )

    # Adjust labels: the kmeans function pass the index of each cluster. We
    # need to associate each index to the corresponding cluster id
    cluster_ids = [cluster.id for cluster in clusters]
    labels = [cluster_ids[idx] for idx in labels]

    # Create a map from cluster to a list of corresponding users
    cluster_map = defaultdict(list)
    cluster_ids = {cluster.id: cluster for cluster in clusters}
    for username, cluster_id in zip(votes.index, labels):
        cluster_map[cluster_id].append(username)
    cluster_map = {cluster_ids[id]: users for id, users in cluster_map.items()}
    math.update_cluster_user_m2m(cluster_map, conversation)

    return update_clusters_original(conversation, clusters, users)


def same_columns(a, b):
    for col in a.columns:
        if col not in b:
            b[col] = float('nan')
    for col in b.columns:
        if col not in a:
            a[col] = float('nan')
