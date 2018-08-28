from ej.components import with_template
from hyperpython.django import csrf_input
from .. import models


@with_template(models.Comment, role='card')
def comment_card(comment, request=None, **kwargs):
    """
    Render comment informations inside a comment card.
    """

    user = getattr(request, 'user', None)
    is_authenticated = getattr(user, 'is_authenticated', False)
    total = comment.conversation.comments.count()
    remaining = comment.conversation.comments.count() - comment.conversation.user_votes(user).count()
    voted = total - remaining + 1
    return {
        'comment': comment,
        'total': total,
        'voted': voted,
        'show_user_actions': is_authenticated,
        'csrf_input': csrf_input(request),
        **kwargs,
    }


@with_template(models.Comment, role='moderate')
def comment_moderate(comment, request=None, **kwargs):
    """
    Render a comment inside a moderation card.
    """

    return {
        'comment': comment,
        'csrf_input': csrf_input(request)
    }
