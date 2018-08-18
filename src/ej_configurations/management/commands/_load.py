import os
import re
from django.utils.text import slugify
from django.contrib.flatpages.models import FlatPage

from pathlib import Path

# Not perfect, but works most of the time ;)
HTML_TITLE_RE = re.compile(r'<h1[^>]*>(?P<title>[^<]*)</h1>')
MARKDOWN_TITLE_RE = re.compile(r'\# (?P<title>[^\n]*)')


def make_url(path):
    name = os.path.splitext(Path(path).name)[0]
    return '/%s/' % '/'.join(slugify(part) for part in name.split('__'))


def make_fragment_name(path):
    path = os.path.splitext(Path(path).name)[0]
    return path.replace('__', '/')


def has_page(name):
    return FlatPage.objects.filter(name=name).exists()


def is_valid_extension(path, exts):
    _, ext = os.path.splitext(path)
    return ext.lower() in exts


def is_html(path):
    return is_valid_extension(path, {'.html', '.htm'})


def is_markdown(path):
    return is_valid_extension(path, {'.md', '.markdown'})


def validate_path(path):
    if not os.path.exists(path):
        raise SystemExit('Path does not exist: %r' % path)
