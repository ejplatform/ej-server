from ej.roles import with_template
from . import models


#
# Conversation roles
#
@with_template(models.Conversation, role='card')
def conversation_card(conversation, request=None, url=None, board=None, **kwargs):
    """
    Render a round card representing a conversation in a list.
    """

    user = getattr(request, 'user', None)
    is_author = conversation.author == user
    moderate_url = None
    return {
        'conversation': conversation,
        'url': url or conversation.get_absolute_url(board=board),
        'tags': conversation.tags.all(),
        'n_comments': conversation.approved_comments.count(),
        'n_votes': conversation.vote_count(),
        'n_followers': conversation.followers.count(),
        'moderate_url': moderate_url,
        'is_author': is_author,
        **kwargs,
    }
