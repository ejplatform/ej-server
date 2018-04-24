import os
from ._load import make_url,is_html, is_markdown, validate_path, HTML_TITLE_RE, MARKDOWN_TITLE_RE
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.contrib.flatpages.models import FlatPage

from django.conf import settings
from pathlib import Path

SITE_ID = getattr(settings, 'SITE_ID', 1)


class Command(BaseCommand):
    help = 'Load HTML/Markdown files as Flatpages'

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
        if not path:
            path = 'local'
        validate_path(path)

        base = Path(path)
        urls = ((p, make_url(p)) for p in os.listdir(path))
        urls = ((base / p, url) for p, url in urls if url)

        # Filter out existing urls
        current_urls = set(FlatPage.objects.values_list('url', flat=True))
        url_map = {}
        for p, url in urls:
            if force or url not in current_urls:
                url_map[url] = p
            else:
                print('Page exists: <base>%s (%s)' % (url, p))

        # Flatpages args
        kwargs = {}

        # Split HTML from markdown
        html_files = {p: url for url, p in url_map.items() if is_html(p)}
        md_files = {p: url for url, p in url_map.items() if is_markdown(p)}
        return [
            *[self.handle_html(*args, kwargs) for args in html_files.items()],
            *[self.handle_markdown(*args, kwargs) for args in md_files.items()],
        ]

    def handle_html(self, path, url, kwargs):
        save_file(path, url, HTML_TITLE_RE,
                  template='flatpages/html.html', **kwargs)

    def handle_markdown(self, path, url, kwargs):
        save_file(path, url, MARKDOWN_TITLE_RE,
                  template='flatpages/markdown.html', **kwargs)


def save_file(path, url, title_re, template, **kwargs):
    data = path.read_text()
    title_m = title_re.match(data)
    title = title_m.groupdict()['title'] if title_m else path.name
    page = FlatPage(url=url, title=title, content=data,
                    template_name=template, **kwargs)
    page.full_clean()
    page.save()
    page.sites.add(Site.objects.get(id=SITE_ID))
    print('Saved page: %s' % page)
    return page

