from pathlib import Path

from boogie.router import Router
from ej_configurations import social_icons
from ej_help.utils import flat_pages_route

app_name = 'ej_help'
urlpatterns = Router(
    template=['ej_help/{name}.jinja2', 'generic.jinja2'],
)



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
