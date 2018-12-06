import random

from django.contrib.auth import get_user_model
from django.db.models import Avg

from ej_clusters.models import Cluster, Stereotype, StereotypeVote
from ej_conversations import create_conversation, Choice
from ej_conversations.models import Vote

User = get_user_model()


def set_clusters_from_comments(conversation, comment_map, exclusive=True, author=None):
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
    clusterization = conversation.get_clusterization()
    created_comments = []
    created_stereotypes = []

    for cluster_name, comments in comment_map.items():
        if isinstance(cluster_name, (tuple, list)):
            cluster_name, description = cluster_name
        else:
            description = f'Stereotype for the "{cluster_name}" cluster'

        # Create cluster and stereotype
        cluster = Cluster.objects.create(
            clusterization=clusterization,
            name=cluster_name,
        )
        stereotype, _ = Stereotype.objects.get_or_create(
            name=cluster_name,
            description=description,
            owner=author,
        )
        cluster.stereotypes.add(stereotype)
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


def cluster_votes(conversation, users):
    clusterization = conversation.get_clusterization()
    comments = list(conversation.comments.all())
    comments_map = {comment.id: comment for comment in comments}
    clusters = {cluster: [] for cluster in clusterization.clusters.all()}
    cluster_list = list(clusters)
    n_clusters = len(cluster_list)

    for i, user in enumerate(users):
        cluster = cluster_list[i % n_clusters]
        clusters[cluster].append(user)

    votes = []
    for cluster, users in clusters.items():
        vote_profiles = (
            StereotypeVote.objects
                .filter(author__in=cluster.stereotypes.all())
                .values('comment')
                .annotate(average=Avg('choice'))
        )
        for data in vote_profiles:
            comment_id = data['comment']
            prob = 0.5 + data['average'] * 0.4

            for user in users:
                vote = random_vote(prob)

                if vote is not None:
                    vote = comments_map[comment_id].vote(user, vote, commit=False)
                    votes.append(vote)

    Vote.objects.bulk_create(votes)


def random_vote(prob):
    r = random.random()
    if r < 0.25:
        return Choice.SKIP
    elif r < 0.50:
        return None
    elif random.random() < prob:
        return Choice.AGREE
    else:
        return Choice.DISAGREE


#
# Examples
#
def make_conversation_with_clusters():
    conversation = create_conversation(
        'How should our society organize the production of goods and services?',
        'Economy',
        is_promoted=True,
        author=User.objects.filter(is_staff=True).first(),
    )
    set_clusters_from_comments(conversation, {
        'Liberal': [
            'Free market should regulate how enterprises invest money and hire '
            'employees.',
            'State should provide a stable judicial system and refrain from '
            'regulating the economy.',
        ],
        'Socialist': [
            'Government and the society as a whole must regulate business '
            'decisions to favor the common good rather than private interests.',
            'State leadership is necessary to drive a strong economy.',
        ],
        'Facist': [
            'Government should eliminate opposition in order to ensure '
            'governability.',
            'Military should occupy high ranks in government.',
        ]
    })
    return conversation
