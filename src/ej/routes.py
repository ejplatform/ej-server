import logging
import os
from pprint import pformat

from boogie.router import Router
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.flatpages.models import FlatPage
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from sidekick import import_later, Proxy

from ej.utils.flatpages import flat_page_route

conversations = import_later('ej_conversations.models:Conversation')
log = logging.getLogger("ej")
urlpatterns = Router(template="pages/{name}.jinja2")


#
# Views
#
@urlpatterns.route("")
def index(request):
    if request.user.is_authenticated:
        return redirect(settings.EJ_USER_HOME_PATH)
    else:
        return redirect(settings.EJ_ANONYMOUS_HOME_PATH)


@urlpatterns.route("start/")
def home(request):
    return {
        'conversations': conversations.objects.promoted(),
        'profile': Proxy(lambda: request.user.profile),
        **home_page_ns,
    }


@urlpatterns.route("info/")
def info(request):
    from ej_conversations.models import Conversation, Comment, Vote

    if not request.user.is_superuser:
        raise Http404

    count = lambda x: x.objects.count()
    return {
        # Generic info
        "user_count": count(get_user_model()),
        "flatpages": FlatPage.objects.values_list("url"),

        # Conversations
        "conversations_counts": {
            _("Conversations"): count(Conversation),
            _("Votes"): count(Vote),
            _("Comments"): count(Comment),
        },
    }


@urlpatterns.route("info/styles/")
def info_styles(request):
    if not request.user.is_superuser:
        raise Http404
    return {}


@urlpatterns.route("info/django-settings/")
def info_django_settings(request):
    if not request.user.is_superuser:
        raise Http404
    data = [
        (name, pformat(getattr(settings, name)))
        for name in dir(settings)
        if name.isupper()
    ]
    return {"settings_data": sorted(data)}


@urlpatterns.route("info/environment/")
def info_environ(request):
    if not request.user.is_superuser:
        raise Http404
    return {"settings_data": sorted(os.environ.items())}


#
# Non-html data
#
@urlpatterns.route("sw.js")
def service_worker(request):
    return render(request, "js/sw.js", {}, content_type="application/javascript")


#
# Static pages
#
urlpatterns.register(
    lambda: {}, "docs/", name="documentation", template="pages/docs.jinja2"
)
urlpatterns.register(flat_page_route("rules"), "rules/")
urlpatterns.register(flat_page_route("faq"), "faq/")
urlpatterns.register(flat_page_route("about-us"), "about-us/")
urlpatterns.register(flat_page_route("usage"), "usage/")

#
# Static data
#
home_page_ns = {
    "people": {
        "alexandre.jpg": "Alexandre Augusto",
        "arthur.jpg": "Arthur Diniz",
        "arthur-jahn.jpg": "Arthur Jahn",
        "aulus.jpg": "Áulus Diniz",
        "bruna.jpg": "Bruna Nayara",
        "bruno.jpg": "Bruno Martin",
        "caio.jpg": "Caio Almeida",
        "carla.jpg": "Carla Rocha",
        "dani.jpg": "Dani Sampaio ",
        "danielhenrique.jpg": "Daniel Henrique",
        "davidcarlos.jpg": "David Carlos",
        "dayanne.jpg": "Dayanne Fernandes",
        "fabiola.jpg": "Fabíola Fleury",
        "fabio.jpg": "Fabio Macedo",
        "fabricio.jpg": "Fabricio Solagna",
        "gabriela.jpg": "Gabriela Alves",
        "gardenia.jpg": "Gardenia Nogueira",
        "guilherme.jpg": "Guilherme Lacerda",
        "heloise.jpg": "Heloise Cullen",
        "henrique.jpg": "Henrique Parra",
        "jonathan.jpg": "Jonathan Moares",
        "laury.jpg": "Laury Bueno",
        "leandro.jpg": "Leandro Nunes",
        "leonardo.jpg": "Leonardo Gomes",
        "luan.jpg": "Luan Guimarães",
        "lucas.jpg": "Lucas Malta",
        "luiza.jpg": "Luiza Peixe",
        "marcela.jpg": "Marcela Rocha",
        "marco.jpg": "Marco William",
        "matheus.jpg": "Matheus Richard",
        "maurilio.jpg": "Maurilio Atila",
        "pablo.jpg": "Pablo Silva",
        "rafa.jpg": "Rafa Ayala",
        "rafael.jpg": "Rafael Makaha",
        "ricardo.jpg": "Ricardo Poppi",
        "rodrigo.jpg": "Rodrigo Oliveira",
        "tallys.jpg": "Tallys Martins",
        "ulf.jpg": "Ulf Treger",
        "vanessa.jpg": "Vanessa Tonini",
    },
    "documentation_items": [
        {
            "href": "/docs/?page=user-start.html",
            "icon": "fa fa-user-circle",
            "text": _("User Guides"),
        },
        {
            "href": "/docs/?page=user-install.html",
            "icon": "fa fa-download",
            "text": _("Installation"),
        },
        {
            "href": "/docs/?page=user-admin.html",
            "icon": "fa fa-cog",
            "text": _("Administration Guides"),
        },
        {
            "href": "/docs/?page=dev.html",
            "icon": "fa fa-code",
            "text": _("Development Guides"),
        },
        {
            "href": "/docs/?page=user-ai.html",
            "icon": "fas fa-microchip",
            "text": _("Our Artificial Intelligence"),
        },
        {
            "href": "/docs/?page=contributing.html",
            "icon": "fab fa-github",
            "text": _("Contributing"),
        },
        {
            "href": "/docs/?page=user-report.html",
            "icon": "far fa-life-ring",
            "text": _("Getting Help"),
        },
    ],
    "partners": [
        {
            "name": "Instituto Cidade Democrática",
            "url": "https://instituto.cidadedemocratica.org.br",
            "img": "cidade.png",
        },
        {
            "name": "LAPPIS",
            "url": "https://lappis.rocks",
            "img": "lappis.png",
        },
        {
            "name": "Hacklab",
            "url": "https://hacklab.com.br",
            "img": "hacklab.png",
        },
        {
            "name": "Pencil Labs",
            "url": "https://pencillabs.com.br",
            "img": "pencil.png",
        },
        {
            "name": "Transparência Internacional",
            "url": "https://transparenciainternacional.org.br",
            "img": "ti.png",
        },
        {
            "name": "Fundação Perseu Abramo",
            "url": "https://fpabramo.org.br",
            "img": "fpa.png",
        },
        {
            "name": "PCdoB",
            "url": "https://pcdob.org.br",
            "img": "pcdob.png",
        },
    ],
}
