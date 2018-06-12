from ej_clusters import math

update_clusters_original = math.update_clusters


def fix():
    math.update_clusters = update_clusters


def update_clusters(conversation, clusters, users=None):
    """
    Assign users to their respective clusters in conversation.
    """
    stereotypes = {cluster: cluster.mean_stereotype() for cluster in clusters}
    votes = get_raw_votes(conversation, comments=comments)

    return update_clusters_original(conversation, clusters, users)

    comments = join_sets(set(x.index) for x in stereotypes.values())
    cluster_map = defaultdict(list)
    user_model = get_user_model()
    username_list = votes['user'].unique()
    if users is not None:
        username_list = [user.username for user in users]

    for user in username_list:
        user_votes = votes[votes['user'] == user]
        user_votes.index = user_votes.pop('comment')
        user_votes.pop('user')

        distances = [
            (float((stereotype - user_votes).mean()), cluster)
            for cluster, stereotype in stereotypes.items()
        ]
        _distance, cluster = min(distances, key=lambda x: x[0])
        cluster_map[cluster].append(user)

    with transaction.atomic():
        for cluster, users in cluster_map.items():
            users = user_model.objects.filter(username__in=users)
            cluster.users.set(users)
