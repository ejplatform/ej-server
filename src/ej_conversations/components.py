from functools import wraps

from django.template.loader import get_template

from hyperpython import Block, Text, h1, p
from hyperpython.components import render, html_list


def join_classes(*args, **kwargs):
    """
    Join classes from several sources.

    Classes can be strings (spaces split different classes)

    >>> join_classes('foo', 'bar baz')
    ['foo', 'bar', 'baz']

    Classes can be lists or mixed

    >>> join_classes('foo', ['bar', 'baz'])
    ['foo', 'bar', 'baz']


    Keywords conditionally adds classes if the argument is true. In Python 3.6+,
    it preserves insertion order

    >>> join_classes(['foo', 'bar'], baz=True, ham=False)
    ['foo', 'bar', 'baz']

    """
    classes = []
    for arg in args:
        if isinstance(arg, str):
            classes.extend(arg.split())
    for cls, value in kwargs.items():
        if value:
            classes.append(cls)
    return classes


def from_template(template_name):
    """
    Register a renderer that uses a Django template to render the content.
    """

    template = get_template(template_name)

    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            ctx = func(*args, **kwargs)
            raw_html = template.render(ctx)
            return Text(raw_html, escape=False)

        return wrapped

    return decorator


def title(title, subtitle=None, class_=(), **kwargs):
    """
    Title with optional subtitle component like in
    https://projects.invisionapp.com/d/main#/console/13863876/300669779/preview
    """

    title = h1(render(title), class_=join_classes('ContentTitle', class_), **kwargs)
    if subtitle is None:
        return Block([title, p(render(subtitle), class_='ContentTitle-subtitle')])
    return title


def configuration_handle(links):
    """
    Renders a configuration handler component like in

    https://projects.invisionapp.com/d/main#/console/13863876/301630843/preview
    """
    return html_list(links)


#
# Configuration elements
#
@render.register('ej_conversations.models.Conversation', role='card')
@from_template('ej_conversations/conversation-card.jinja2')
def conversation_card(conversation):
    """
    A simple card that represents small detail about a conversation.
    """
    return {
        'conversation': conversation,
    }
