from pathlib import Path

from django.contrib.flatpages.models import FlatPage
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

REPO = Path(__file__).parent.parent.parent
LIB = REPO / 'lib/resources/pages/'


def flat_pages_route(slug):
    def route(request):
        try:
            page = FlatPage.objects.get(url=f'/{slug}/')
        except FlatPage.DoesNotExist:
            page = fallback_page(slug)
        return render(request, page.template_name, {'flatpage': page})

    route.__name__ = route.__qualname__ = slug
    return route


def fallback_page(slug):
    md = LIB / f'{slug}.md'
    html = LIB / f'{slug}.html'
    if html.exists():
        data = open(html).read()
        return FlatPage(content=data, title=slug, template_name='flatpages/html.html')
    elif md.exists():
        data = open(md).read()
        return FlatPage(content=data, title=slug, template_name='flatpages/markdown.html')
    else:
        data = _('Page {slug} not found').format(slug=slug)
        return FlatPage(content=data, title=slug, template_name='flatpages/html.html')
