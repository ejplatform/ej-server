import logging

from django.shortcuts import render, redirect, HttpResponse
from django.utils.translation import ugettext_lazy as _

from boogie.router import Router
from ej_configurations import fragment, social_icons
from ej_conversations.models import Conversation
from ej_conversations import rules


log = logging.getLogger('ej')
urlpatterns = Router()


#
# Views
#
@urlpatterns.route('')
def home(request):
    conversations = []
    for conversation in Conversation.objects.all():
        conversations.append(
            (conversation, rules.is_owner(request.user, conversation))
        )
    ctx = {
        'conversations': conversations,
        'home_banner_fragment': fragment('home.banner', raises=False),
        'how_it_works_fragment': fragment('home.how-it-works', raises=False),
        'start_now_fragment': fragment('home.start-now', raises=False),
        'social_media_icons': social_icons(),
    }
    return render(request, 'pages/home.jinja2', ctx)
        

@urlpatterns.route('start/')
def start(request):
    if request.user.id:
        return redirect('/conversations/')
    return redirect('/login/')


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
