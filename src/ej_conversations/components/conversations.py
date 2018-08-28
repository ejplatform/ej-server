from ej.components import with_template
from hyperpython.django import csrf_input
from .. import models


@with_template(models.Conversation, role='card')
def conversation_card(conversation, request=None, url=None, **kwargs):
    """
    Render a round card representing a conversation in a list.
    """

    user = getattr(request, 'user', None)
    is_author = conversation.author == user
    moderate_url = None
    return {
        'conversation': conversation,
        'url': url or conversation.get_absolute_url(),
        'tags': conversation.tags.all(),
        'n_comments': conversation.comments.count(),
        'n_votes': conversation.vote_count(),
        'n_followers': conversation.followers.count(),
        'moderate_url': moderate_url,
        'is_author': is_author,
        **kwargs,
    }


@with_template(models.Conversation, role='balloon')
def conversation_balloon(conversation, request=None, **kwargs):
    """
    Render details of a conversation inside a conversation balloon.
    """

    user = getattr(request, 'user', None)
    favorites = models.FavoriteConversation.objects
    is_authenticated = getattr(user, 'is_authenticated', False)
    is_favorite = is_authenticated and conversation.is_favorite(user)
    return {
        'conversation': conversation,
        'tags': conversation.tags.all(),
        'comments_count': conversation.comments.count(),
        'votes_count': conversation.votes.count(),
        'favorites_count': favorites.filter(conversation=conversation).count(),
        'user': user,
        'csrf_input': csrf_input(request),
        'show_user_actions': is_authenticated,
        'is_favorite': is_favorite,
        **kwargs,
    }
