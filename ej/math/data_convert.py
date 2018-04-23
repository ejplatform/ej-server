import pandas as pd

from ej_conversations.models import Vote


def get_votes(conversation, comments=None):
    """
    Create a pandas data frame completely describing the given conversation.

    Args:
        conversation:
            A conversation object.
        comments:
            If given, it its treated as a list of comments. Otherwise, uses all comments
            for the conversation.

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
            .values_list('comment_id', 'author__username', 'value')
    )
    return build_dataframe(votes, comment_ids, fillna=0)


def get_votes_with_stereotypes(conversation, comments=None):
    """
    Like get_votes(), but return two dataframes (df_votes, df_stereotype_votes),
    the second being the votes cast by the stereotypes.
    """
    if comments is None:
        comments = conversation.comments.all()

    user_votes = get_votes(conversation, comments)

    # Fetch all votes in a single query
    comment_ids = comments.values_list('id', flat=True)
    votes = (
        Vote.objects
            .filter(comment_id__in=comments)
            .values_list('comment_id', 'stereotype__name', 'value')
    )
    stereotype_votes = build_dataframe(votes, comment_ids, fillna=0)
    return user_votes, stereotype_votes


def build_dataframe(items, columns, fillna=None):
    """
    Convert a list of (column, index, value) items into a data frame.
    """
    # Group by comment_id
    groups = {comment: [] for comment in columns}
    for col, index, value in items:
        groups[col].append((index, value))

    # Insert on data frame
    df = pd.DataFrame()
    for col in columns:
        column = pd.Series(dict(groups[col]))
        df[col] = column

    if fillna is not None:
        df.fillna(0, inplace=True)
    return df
