import logging

from django.conf import settings
from django.shortcuts import render, redirect

from boogie.router import Router
from ej_configurations import fragment, social_icons
from ej_conversations.models import Conversation
from ej_boards.models import Board

log = logging.getLogger('ej')
urlpatterns = Router(
    template='pages/{name}.jinja2',
)


#
# Views
#
@urlpatterns.route('')
def index(request):
    if request.user.id:
        return redirect(settings.EJ_USER_HOME_PATH)
    else:
        return redirect(settings.EJ_ANONYMOUS_HOME_PATH)

@urlpatterns.route('start/')
def start(request):
    return {
        'conversations': Conversation.objects.promoted(),
        'how_it_works_fragment': fragment('home.how-it-works', raises=False),
        'start_now_fragment': fragment('home.start-now', raises=False),
        'social_media_icons': social_icons(),
        'user': request.user,
        'footer_content': {
            'image': '/static/img/icons/facebook-blue.svg',
            'first': {'normal': 'Plataforma desenvolvida pelo', 'bold': 'Conanda/MDH/UnB'},
            'last': {'normal': 'Para denunciar:', 'bold': 'Disque 100 e #HUMANIZAREDES'}
        },
    }


@urlpatterns.route('menu/')
def menu(request):
    return {
        'user': request.user,
    }


#
# Non-html data
#
@urlpatterns.route('sw.js')
def service_worker(request):
    return render(request, 'js/sw.js', {}, content_type='application/javascript')


#
# Static pages
#
urlpatterns.route('home/', name='home', template='pages/home.jinja2')(lambda: {})
urlpatterns.route('docs/', name='documentation', template='pages/docs.jinja2')(lambda: {})
