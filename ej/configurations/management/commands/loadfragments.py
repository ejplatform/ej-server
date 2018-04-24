import os
from pathlib import Path
from ._load import make_url, is_html, is_markdown, validate_path, MARKDOWN_TITLE_RE, HTML_TITLE_RE
from django.core.management.base import BaseCommand
from ...models import Fragment
from django.conf import settings
from django.core.exceptions import ValidationError

SITE_ID = getattr(settings, 'SITE_ID', 1)


class Command(BaseCommand):
    help = 'Load HTML/Markdown files as Fragments, that are some parts of a site'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='Path to look for pages',
        )

    def handle(self, *args, path=False, force=False, **options):
        if not path:
            path = 'local'
        validate_path(path)

        base = Path(path)
        urls = ((base/p, make_url(p)) for p in os.listdir(path))

        # TODO: Filter out existing fragments
        # Fragments don't have unique urls, then url will never be in 'name'

        # Split HTML from markdown
        html_files = {p: url for p, url in urls if is_html(p)}
        md_files = {p: url for p, url in urls if is_markdown(p)}
        return [
            *[self.handle_html(*args) for args in html_files.items()],
            *[self.handle_markdown(*args) for args in md_files.items()],
        ]

    def handle_html(self, path, url):
        save_fragment(path, HTML_TITLE_RE, Fragment.FORMAT_HTML)

    def handle_markdown(self, path, url):
        save_fragment(path, MARKDOWN_TITLE_RE, Fragment.FORMAT_MARKDOWN)


def save_fragment(path, name_re, fragment_format):
    data = path.read_text()
    name_m = name_re.match(data)
    name = name_m.groupdict()['title'] if name_m else path.name
    fragment = Fragment(name=name, format=fragment_format, content=data, editable=True,
                        deletable=True)

    fragment.full_clean()
    fragment.save()
    print('Saved fragment: %s' % fragment)


    return fragment




