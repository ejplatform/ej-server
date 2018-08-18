import logging

from django.conf import settings
from django.shortcuts import render, redirect

from boogie.router import Router
from ej_configurations import fragment, social_icons
from ej_conversations.proxy import conversations_with_moderation

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
        'conversations': conversations_with_moderation(request.user),
        'home_banner_fragment': fragment('home.banner', raises=False),
        'how_it_works_fragment': fragment('home.how-it-works', raises=False),
        'start_now_fragment': fragment('home.start-now', raises=False),
        'social_media_icons': social_icons(),
        'user': request.user,
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
urlpatterns.route('comments/', name='comments', template='pages/comments.jinja2')(lambda: {})
urlpatterns.route('notifications/', name='notifications', template='pages/notifications.jinja2')(lambda: {})
urlpatterns.route('home/', name='home', template='pages/home.jinja2')(lambda: {})
