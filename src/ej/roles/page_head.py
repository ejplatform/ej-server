from hyperpython import meta
from hyperpython.components import Head as BaseHead

from ej.roles.tags import static


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
            None: static('img/logo/logo.svg'),
            16: static('img/logo/icon-16.png'),
            32: static('img/logo/icon-32.png'),
            57: static('img/logo/icon-57.png'),
            72: static('img/logo/icon-72.png'),
            96: static('img/logo/icon-96.png'),
            114: static('img/logo/icon-114.png'),
            192: static('img/logo/icon-192.png'),
        })

    def favicon_tags(self):
        return [
            *super().favicon_tags(),
            meta(name='image', content=static('img/logo/logo.svg')),
        ]
