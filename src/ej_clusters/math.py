import operator as op
from collections import defaultdict
from functools import reduce

import pandas as pd
from django.contrib.auth import get_user_model
from django.db import transaction

from ej_conversations.models import Vote
from .models import StereotypeVote


def get_votes(conversation, comments=None, fillna=None):
    """
    Create a pandas data frame with all votes for the given conversation.

    Args:
        conversation:
            A conversation object.
        comments:
            If given, it its treated as a list of comments. Otherwise, uses all
            comments for the conversation.

    Returns:
        A data frame indexed by the username who cast each vote and with comment
        id in the columns.
    """
    votes = get_raw_votes(conversation, comments)
    return build_dataframe(votes, fillna=fillna)


def get_raw_votes(conversation, comments=None):
    """
    Return a data frame with the raw list of votes.

    The resulting data frame has 3 columns, user, comment and vote, that
    specifies the username, comment id and choice for each vote cast in the
    conversation.
    """
    if comments is None:
        comments = conversation.comments.all()

    # Fetch all votes in a single query
    filter = {'comment__in': comments}
    values = ['author__username', 'comment_id', 'choice']
    items = Vote.objects.filter(**filter).values_list(*values)
    return pd.DataFrame(list(items), columns=['user', 'comment', 'choice'])


def get_votes_with_stereotypes(conversation, comments=None, fillna=None):
    """
    Like get_votes(), but return two dataframes (df_votes, df_stereotype_votes),
    the second representing votes cast by stereotypes.
    """
    if comments is None:
        comments = conversation.comments.all()

    user_votes = get_votes(conversation, comments)

    # Fetch all votes in a single query
    filter = {'comment__in': comments}
    values = ['author__username', 'comment_id', 'choice']
    votes = StereotypeVote.objects.filter(**filter).values_list(*values)
    stereotype_votes = build_dataframe(votes, fillna=fillna)
    return user_votes, stereotype_votes


def build_dataframe(df, fillna=None):
    """
    Convert a list of (column, index, value) items into a data frame.
    """
    pivot = df.pivot(index='user', columns='comment', values='choice')
    if fillna is not None:
        pivot.fillna(fillna, inplace=True)
        pivot = pivot.astype('uint8')
    return pivot


def update_clusters(conversation, clusters, users=None):
    """
    Assign users to their respective clusters in conversation.
    """

    stereotypes = {cluster: cluster.mean_stereotype() for cluster in clusters}
    comments = join_sets(set(x.index) for x in stereotypes.values())
    votes = get_raw_votes(conversation, comments=comments)
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


def join_sets(sets):
    return reduce(op.or_, sets)
