import pandas as pd

from ej_conversations.models import Vote


def get_votes(conversation, comments=None, fillna=None):
    """
    Create a pandas data frame describing the given conversation.

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
    if comments is None:
        comments = conversation.comments.all()

    # Fetch all votes in a single query
    comment_ids = comments.values_list('id', flat=True)
    votes = (
        Vote.objects
            .filter(comment_id__in=comment_ids)
            .values_list('author__username', 'comment_id', 'value')
    )
    return build_dataframe(votes, fillna=fillna)


def get_votes_with_stereotypes(conversation, comments=None, fillna=None):
    """
    Like get_votes(), but return two dataframes (df_votes, df_stereotype_votes),
    the second representing votes cast by stereotypes.
    """
    if comments is None:
        comments = conversation.comments.all()

    user_votes = get_votes(conversation, comments)

    # Fetch all votes in a single query
    comment_ids = comments.values_list('id', flat=True)
    votes = (
        Vote.objects
            .filter(comment_id__in=comments)
            .values_list('author__username', 'comment_id', 'value')
    )
    stereotype_votes = build_dataframe(votes, fillna=fillna)
    return user_votes, stereotype_votes


def build_dataframe(items, fillna=None):
    """
    Convert a list of (column, index, value) items into a data frame.
    """

    df = pd.DataFrame(items, columns=['user', 'comment', 'vote'])
    pivot = df.pivot(index='user', columns='comment', values='vote')
    if fillna is not None:
        pivot.fillna(fillna, inplace=True)
        pivot = pivot.astype('uint8')
    return pivot
