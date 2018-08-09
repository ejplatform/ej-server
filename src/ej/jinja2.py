import os
import random
import string

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils import translation
from jinja2 import Environment, StrictUndefined, contextfunction
from markdown import markdown
from markupsafe import Markup

import hyperpython.jinja2
from ej_configurations import social_icons, fragment
from hyperpython import render
from . import components
from .components import tags

TAG_MAP = {k: getattr(tags, k) for k in tags.__all__}
SALT_CHARS = string.ascii_letters + string.digits + '-_'


def environment(**options):
    options.pop('debug', None)
    options.setdefault('trim_blocks', True)
    options.setdefault('lstrip_blocks', True)
    options['undefined'] = StrictUndefined
    env = Environment(**options)
    theme = 'default'
    if 'THEME' in os.environ:
        theme = os.environ['THEME']

    env.globals.update(
        static=staticfiles_storage.url,
        url=reverse,
        settings=settings,

        # Security
        salt_attr=salt_attr,
        salt_tag=salt_tag,
        salt=salt,

        # Platform functions
        social_icons=social_icons,
        fragment=fragment,
        service_worker=getattr(settings, 'SERVICE_WORKER', False),
        current_theme=theme,
        context=context,

        # Hyperpython tag functions
        render=non_strict_render,

        # Available tags and components
        tag=components,
        **TAG_MAP,
    )
    env.filters.update(
        markdown=lambda x: Markup(markdown(x)),
        pc=format_percent,
        salt=salt,
        **hyperpython.jinja2.filters,
    )
    env.install_gettext_translations(translation, newstyle=True)
    return env


#
# String formatting
#
def format_percent(x):
    return f'{int(x * 100)}%'


#
# Security
#
def salted(value):
    """
    Protects a value using a random salt. This completely prevents the BREACH
    attack against a salted secret, but stores values in a codified form that
    cannot be directly used.

    The BREACH authors suggest a transform that takes a string P and returns
    (P + (S^P)), where S^P is a XOR operation of each byte. Templates do not
    have a byte-level control of the message, hence salting must be done in
    unicode data. This brings some problems:

    * How to (efficiently) implement XOR for a large alphabet such as unicode?
    * Xor-ing two valid unicode points will not necessarily yield a valid
      unicode value.
    * Client code needs to recover the encoded data, hence the solution must
      be portable to Python and Javascript
    """
    # TODO: how to do it with unicode?
    raise NotImplementedError


def salt(size=None):
    """
    Create a random string of characters of a random size.

    The goal of the random salt is to make it more difficult to execute a
    BREACH attack (https://docs.djangoproject.com/en/2.0/ref/middleware/#module-django.middleware.gzip).
    A random salt makes the attack more difficult by requiring more requests to
    correctly guess each byte in the target secret sub-string.
    """
    size = random.randint(4, 10) if size is None else size
    func = random.choice
    chars = SALT_CHARS
    return ''.join(func(chars) for _ in range(size))


def salt_attr():
    """
    A salt added as an HTML attribute.
    """
    return f'data-salt="{salt()}"'


def salt_tag():
    """
    A salt added as an invisible HTML tag.
    """
    return f'<div style="display: none" {salt_attr()}></div>'


@contextfunction
def context(ctx):
    """
    Renders the current context as a description list.
    """
    blacklist = {
        # Jinja2
        'range', 'dict', 'lipsum', 'cycler', 'joiner', 'namespace', '_',
        'gettext', 'ngettext', 'request', 'csrf_input', 'csrf_token',

        # Globals
        'static', 'url', 'salt_attr', 'salt_tag', 'salt', 'social_icons',
        'service_worker', 'context', 'render', *TAG_MAP,

        # Variables injected by the base template
        'target', 'target_context',
        'sidebar', 'page_top_header', 'page_header',
        'page_title', 'title', 'content_title',
    }
    ctx = {k: v for k, v in ctx.items() if k not in blacklist}
    return tags.html_map(ctx)


def non_strict_render(obj, role=None, ctx=None, strict=False):
    return render(obj, role=role, ctx=ctx, strict=strict)
