from ej_clusters.models import Cluster, Stereotype, StereotypeClusterMap, UserClusterMap


def set_clusters_from_comments(conversation, comment_map, exclusive=True,
                               author=None):
    """
    Create clusters and stereotypes from conversation.

    Usage:

        >>> set_clusters_from_comments(conversation, {
            'cluster1': [
                'stereotype comment for cluster 1',
                'alternative stereotype comment for cluster 1',
            ]
            'cluster2': [
                'stereotype comment for cluster 2',
            ]
        })
    """
    author = author or conversation.author
    created_comments = []
    created_stereotypes = []

    for cluster_name, comments in comment_map.items():
        if isinstance(cluster_name, (tuple, list)):
            cluster_name, description = cluster_name
        else:
            description = f'Stereotype for the "{cluster_name}" cluster'

        # Create cluster and stereotype
        cluster = Cluster.objects.create(
            conversation=conversation,
            name=cluster_name,
        )
        stereotype, _ = Stereotype.objects.get_or_create(
            name=cluster_name,
            description=description,
        )
        StereotypeClusterMap.objects.create(
            stereotype=stereotype,
            cluster=cluster,
            conversation=conversation,
        )
        created_stereotypes.append(stereotype)

        # Save comments for stereotype
        if isinstance(comments, str):
            comments = [comments]
        for text in comments:
            comment = conversation.create_comment(
                author, text,
                status='approved',
                check_limits=False,
            )
            created_comments.append(comment)
            stereotype.vote(comment, 'agree')

    if exclusive:
        for stereotype in created_stereotypes:
            voted_ids = stereotype.votes.values_list('comment_id', flat=True)
            votes = {
                comment: 'disagree'
                for comment in created_comments if comment.id not in voted_ids
            }
            stereotype.cast_votes(votes)

    return created_comments


def set_clusters(conversation, stereotype_map=None, user_map=None, clean=False):
    """
    Update cluster
    """
    user_map = user_map or {}
    stereotype_map = stereotype_map or {}
    cluster_names = set()
    cluster_names.update(user_map.values())
    cluster_names.update(stereotype_map.values())

    if clean:
        UserClusterMap.objects.filter(conversation=conversation).delete()
        StereotypeClusterMap.objects.filter(conversation=conversation).delete()

    clusters = {
        k: Cluster.objects.get_or_create(conversation=conversation, name=k)[0]
        for k in cluster_names
    }

    factory = UserClusterMap.objects.create
    for user, cluster_name in user_map.items():
        cluster = clusters[cluster_name]
        factory(user=user, conversation=conversation, cluster=cluster)

    factory = StereotypeClusterMap.objects.create
    for user, cluster_name in stereotype_map.items():
        cluster = clusters[cluster_name]
        factory(stereotype=user, conversation=conversation, cluster=cluster)

    return list(clusters.values())


def update_clusters(conversation, users=None):
    """
    Assign users to their respective clusters in conversation.
    """

