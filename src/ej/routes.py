import logging

from django.shortcuts import render, redirect

from boogie.router import Router
from ej_configurations import fragment, social_icons
from ej_conversations.models import Conversation
from ej.utils.perms import conversations

log = logging.getLogger('ej')
urlpatterns = Router(
    template='pages/{name}.jinja2',
)


#
# Views
#
@urlpatterns.route('')
def home(request):
    if request.user.id:
        return redirect('/conversations/')
    return redirect('/start/')


@urlpatterns.route('start/')
def start(request):
    return {
        'conversations': conversations(
            request.user,
            [rules.can_moderate_conversation],
        ),
        'home_banner_fragment': fragment('home.banner', raises=False),
        'how_it_works_fragment': fragment('home.how-it-works', raises=False),
        'start_now_fragment': fragment('home.start-now', raises=False),
        'social_media_icons': social_icons(),
        'user': request.user,
    }


@urlpatterns.route('clusters/')
def clusters(request):
    ctx = dict(
        content_html='<h1>Error</h1><p>Not implemented yet!</p>'
    )
    return render(request, 'base.jinja2', ctx)


#
# Non-html data
#
@urlpatterns.route('sw.js')
def service_worker(request):
    return render(request, 'js/sw.js', {}, content_type='application/javascript')


#
# Static pages
#
urlpatterns.route('menu/', name='menu', template='pages/menu.jinja2')(lambda: {})
urlpatterns.route('comments/', name='comments', template='pages/comments.jinja2')(lambda: {})
urlpatterns.route('notifications/', name='notifications', template='pages/notifications.jinja2')(lambda: {})
