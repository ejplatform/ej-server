import random
import string

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils import translation
from jinja2 import Environment
from markdown import markdown
from markupsafe import Markup

from ej_configurations import social_icons, fragment
from . import tags

SALT_CHARS = string.ascii_letters + string.digits + '-_'


def environment(**options):
    options.pop('debug', None)
    options.setdefault('trim_blocks', True)
    options.setdefault('lstrip_blocks', True)
    env = Environment(**options)
    env.globals.update(
        static=staticfiles_storage.url,
        url=reverse,
        salt_attr=salt_attr,
        salt_tag=salt_tag,
        salt=salt,
        social_icons=social_icons,
        footer_data=lambda: fragment('global.footer', raises=False),
        service_worker=getattr(settings, 'SERVICE_WORKER', False),
        link=tags.link,
        action_button=tags.action_button,
        rocket_button=tags.rocket_button,
    )
    env.filters.update(
        markdown=lambda x: Markup(markdown(x)),
        pc=format_percent,
        salt=salt,
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
