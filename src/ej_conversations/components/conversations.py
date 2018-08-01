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

        return render.register_template(model, template, role)(func)

    return decorator


@with_template(models.Conversation)
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
