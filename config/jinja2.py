from markdown import markdown
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils.translation import ugettext, ungettext
from jinja2 import Environment
from markupsafe import Markup


def environment(**options):
    options.pop('debug', None)
    env = Environment(**options)
    env.globals.update(
        static=staticfiles_storage.url,
        url=reverse,
    )
    env.filters.update(
        markdown=lambda x: Markup(markdown(x)),
    )
    env.install_gettext_callables(ugettext, ungettext, newstyle=True)
    return env
