from django.contrib.flatpages.models import FlatPage
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from boogie.router import Router
from ej_configurations import social_icons

urlpatterns = Router(
    template='ej_help/{name}.jinja2',
)


def from_flatpage(url):
    def view(request):
        try:
            page = FlatPage.objects.get(url=url)
        except FlatPage.DoesNotExist:
            raise ImproperlyConfigured(
                _(f'Please define a {url} flat page in the site Admin'),
            )
        return render(request, page.template_name, {'page': page})

    return view


@urlpatterns.route('start/')
def start():
    return {}


@urlpatterns.route('rules/')
def rules():
    return {}


@urlpatterns.social('social/')
def social():
    return {'icons': social_icons()}


urlpatterns.register(from_flatpage('faq'), 'faq/')
urlpatterns.register(from_flatpage('about'), 'about/')
urlpatterns.register(from_flatpage('usage'), 'usage/')
