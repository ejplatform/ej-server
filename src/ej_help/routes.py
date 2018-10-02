from pathlib import Path

from django.contrib.flatpages.models import FlatPage
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from boogie.router import Router
from ej_configurations import social_icons

app_name = 'ej_help'
urlpatterns = Router(
    template=['ej_help/{name}.jinja2', 'generic.jinja2'],
)

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


@urlpatterns.route('start/')
def start():
    return {}


@urlpatterns.route('social/')
def social():
    return {'icons': social_icons()}


urlpatterns.register(flat_pages_route('rules'), 'rules/')
urlpatterns.register(flat_pages_route('faq'), 'faq/')
urlpatterns.register(flat_pages_route('about-us'), 'about-us/')
urlpatterns.register(flat_pages_route('usage'), 'usage/')
