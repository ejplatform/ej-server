import pandas as pd

from ej_conversations.models import Vote

StereotypeVote = Vote


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
    filter = dict(comment_id__in=comments.values_list('id', flat=True))
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
    filter = dict(comment_id__in=comments.values_list('id', flat=True))
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


def update_clusters(conversation, users=None):
    """
    Assign users to their respective clusters in conversation.
    """
