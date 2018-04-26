import os
from pathlib import Path
from ._load import make_fragment_name, is_html, is_markdown, validate_path, MARKDOWN_TITLE_RE, HTML_TITLE_RE
from django.core.management.base import BaseCommand
from ...models import Fragment
from django.conf import settings

SITE_ID = getattr(settings, 'SITE_ID', 1)


class Command(BaseCommand):
    help = 'Load HTML/Markdown files as Fragments, that are some parts of a site'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='Path to look for pages',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Override existing pages with file data.',
        )

    def handle(self, *args, path=False, force=False, **options):
        real_handle(path, force)


def real_handle(path, force):
    if not path:
        path = 'local'
    validate_path(path)

    base = Path(path)
    files = ((base/path, make_fragment_name(path)) for path in os.listdir(path))

    # Filter out existing fragments
    current_fragments = list(Fragment.objects.values_list('name'))
    current_fragments = list(map(''.join, current_fragments))

    new_fragments = {}
    for path, name in files:
        if force or name not in current_fragments:
            new_fragments[name] = path
        else:
            print('Fragment exists: <base>%s (%s)' % (name, path))
    

    # Split HTML from markdown
    html_files = {path: name for name, path in new_fragments.items() if is_html(path)}
    md_files = {path: name for name, path in new_fragments.items() if is_markdown(path)}

    return [
        *[handle_html(*args) for args in html_files.items()],
        *[handle_markdown(*args) for args in md_files.items()],
    ]


def handle_html(path, name):
    save_fragment(path,name, Fragment.FORMAT_HTML)


def handle_markdown(path, name):
    save_fragment(path, name, Fragment.FORMAT_MARKDOWN)


def save_fragment(path, name, fragment_format):
    data = path.read_text()
    fragment, created = Fragment.objects.update_or_create(
        name=name,
        defaults={'format': fragment_format,
                  'content': data,
                  'editable': True,
                  'deletable': True,
                  }
    )

    if(created):
        print('Saved fragment: %s' % fragment)
    else:
        print('Updated fragment: %s' % fragment)

    return fragment




