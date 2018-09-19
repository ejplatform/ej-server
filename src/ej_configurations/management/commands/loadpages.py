import os
from pathlib import Path

from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from ._load import make_url, is_html, is_markdown, validate_path, HTML_TITLE_RE, MARKDOWN_TITLE_RE

SITE_ID = getattr(settings, 'SITE_ID', 1)


class Command(BaseCommand):
    help = 'Load HTML/Markdown files as Flatpages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path', '-p',
            type=str,
            help='Path to look for pages',
        )
        parser.add_argument(
            '--force', '-f',
            action='store_true',
            help='Override existing pages with file data.',
        )

    def handle(self, *args, path=None, force=False, **options):
        if not path:
            path = Path('lib/resources/pages/')
        real_handle(path, force)


def real_handle(path, force=False):
    validate_path(path)
    base = Path(path)
    files = ((base / path, make_url(path)) for path in os.listdir(path))

    # Filter out existing urls
    saved_pages = list(FlatPage.objects.values_list('url', flat=True))
    saved_pages = list(map(''.join, saved_pages))
    new_pages = {}
    for path, name in files:
        if force or name not in saved_pages:
            new_pages[name] = path
        else:
            print('Page exists: %s    (%s)' % (name, path))

    # Flatpages args
    kwargs = {}

    # Split HTML from markdown
    html_files = {path: name for name, path in new_pages.items() if is_html(path)}
    md_files = {path: name for name, path in new_pages.items() if is_markdown(path)}
    return [
        *[handle_html(*args, kwargs) for args in html_files.items()],
        *[handle_markdown(*args, kwargs) for args in md_files.items()],
    ]


def handle_html(path, file_name, kwargs):
    save_file(path, file_name, HTML_TITLE_RE,
              template='flatpages/html.html', **kwargs)


def handle_markdown(path, file_name, kwargs):
    save_file(path, file_name, MARKDOWN_TITLE_RE,
              template='flatpages/markdown.html', **kwargs)


def save_file(path, file_name, title_re, template, **kwargs):
    data = path.read_text()
    title_m = title_re.match(data)
    title = title_m.groupdict()['title'] if title_m else path.name
    data = data.replace(title, '', 1)  # remove title from content page
    page, created = FlatPage.objects.update_or_create(
        url=file_name,
        defaults={'title': title,
                  'content': data,
                  'template_name': template
                  },
        **kwargs)
    page.sites.add(Site.objects.get(id=SITE_ID))

    if created:
        print(f'Saved page: {page}    ({path})')
    else:
        print(f'Updated page: {page}    ({path})')

    return page
