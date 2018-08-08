from django.middleware.csrf import get_token

from hyperpython import input_
from hyperpython.components import render
from .. import models


def with_template(model, role=None, template=None):
    """
    Register element rendered from a template.
    """

    def decorator(func):
        nonlocal role, template

        if template is None:
            template = f"ej/roles/{func.__name__.replace('_', '-')}.jinja2"
        if role is None:
            role = func.__name__.rpartition('_')[-1]

        return render.register_template(model, template, role=role)(func)

    return decorator


def csrf_input(request):
    value = '' if request is None else get_token(request)
    return input_(type='hidden', name='csrfmiddlewaretoken', value=value)


@with_template(models.Conversation, role='card', template='ej/roles/conversation-card.jinja2')
def conversation_card(conversation, url=None, request=None, **kwargs):
    """
    Render a round card representing a conversation in a list.
    """

    moderate_url = None
    return {
        'conversation': conversation,
        'url': url or conversation.get_absolute_url(),
        'tags': conversation.tags.all(),
        'n_comments': conversation.comments.count(),
        'n_votes': conversation.vote_count(),
        'n_followers': conversation.followers.count(),
        'moderate_url': moderate_url,
        **kwargs,
    }


@with_template(models.Conversation, role='balloon', template='ej/roles/conversation-balloon.jinja2')
def conversation_balloon(conversation, request=None, **kwargs):
    """
    Render details of a conversation inside a conversation balloon.
    """

    user = getattr(request, 'user', None)
    favorites = models.FavoriteConversation.objects
    is_favorite = False if user is None else conversation.is_favorite(user)
    return {
        'conversation': conversation,
        'tags': conversation.tags.all(),
        'comments_count': conversation.comments.count(),
        'votes_count': conversation.votes.count(),
        'favorites_count': favorites.filter(conversation=conversation).count(),
        'user': user,
        'csrf_input': csrf_input(request),
        'show_user_actions': getattr(user, 'is_authenticated', False),
        'is_favorite': is_favorite,
        **kwargs,
    }
