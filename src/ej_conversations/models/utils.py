def votes_counter(choice):
    if choice is not None:
        return lambda comment: comment.votes.filter(choice=choice).count()
    else:
        return lambda comment: comment.votes.count()


def normalize_status(value):
    """
    Convert status string values to safe db representations.
    """
    from ej_conversations.models import Comment

    if value is None:
        return Comment.STATUS.pending
    try:
        return Comment.STATUS_MAP[value.lower()]
    except KeyError:
        raise ValueError(f'invalid status value: {value}')
