import logging

from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.translation import ugettext_lazy

from hyperpython import a, i, meta
from hyperpython import h
from hyperpython.components import html_table, html_list, html_map, Head as BaseHead, render

static = staticfiles_storage.url
lazy_string_class = type(ugettext_lazy('hello'))
log = logging.getLogger('ej')
_ = lambda x: x

__all__ = [
    # Hyperpython components
    'h', 'html_table', 'html_list', 'html_map',

    # EJ components
    'link', 'rocket_button', 'action_button',
]


def link(value, href='#', target='.Page-mainContainer', class_=(),
         action='target', instant=True, button=False, transition='cross-fade',
         preload=False, scroll=False, prefetch=False, primary=False, args=None):
    classes = [*class_]
    if button:
        classes.append('Button')

    kwargs = {
        'href': href,
        'class': classes,
        'primary': primary,
        'up-instant': instant,
        'up-restore-scroll': scroll,
        'up-preload': preload,
        'up-prefetch': prefetch,
    }
    if action:
        kwargs[f'up-{action}'] = target
    if transition:
        kwargs['up-transition'] = transition
    if args:
        for arg in args.split():
            kwargs[arg] = True
    return a(kwargs, value)


def rocket_button(value=_('Access CPA panel'), href='/talks/', **kwargs):
    return link(href=href, class_="RocketButton", **kwargs)[
        i(value, class_='fa fa-comment')
    ]


def action_button(value=_('Go!'), href='#', primary=True, **kwargs):
    return link(value, href, primary=primary, **kwargs)


class Head(BaseHead):
    """
    Base information describing the <head> tag of a page.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.stylesheets = [
            *self.stylesheets,
            'https://fonts.googleapis.com/css?family=Raleway:400,700,900&subset=latin-ext',
            'https://unpkg.com/unpoly@0.54.0/dist/unpoly.min.css',
            static('css/fontawesome-all.min.css'),
            static('js/jquery-ui/jquery-ui.min.css'),
            static('js/jquery-ui/jquery-ui.structure.min.css'),
            static('css/main.css'),
        ]
        self.scripts = [
            'https://code.jquery.com/jquery-3.2.1.slim.min.js',
            'https://unpkg.com/unpoly@0.54.0/dist/unpoly.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.9.0/slick.min.js',
            static('js/jquery-ui/jquery-ui.min.js'),
            static('js/main.js'),
        ]
        self.favicons = dict(self.favicons)
        self.favicons.update({
            None: static('default/img/logo/logo.svg'),
            16: static('default/img/logo/icon-16.png'),
            32: static('default/img/logo/icon-32.png'),
            57: static('default/img/logo/icon-57.png'),
            72: static('default/img/logo/icon-72.png'),
            96: static('default/img/logo/icon-96.png'),
            114: static('default/img/logo/icon-114.png'),
            192: static('default/img/logo/icon-192.png'),
        })

    def favicon_tags(self):
        return [
            *super().favicon_tags(),
            meta(name='image', content=static('default/img/logo/logo.svg')),
        ]


@render.register(lazy_string_class)
def _render_lazy_string(st, **kwargs):
    return render(str(st))
