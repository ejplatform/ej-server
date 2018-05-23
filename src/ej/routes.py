import logging

from django.shortcuts import render, redirect, HttpResponse
from django.utils.translation import ugettext_lazy as _

from boogie.router import Router
from ej_configurations import fragment, social_icons
from ej_conversations.models import Conversation, Category
from .forms import ConversationForm

log = logging.getLogger('ej')
urlpatterns = Router()


#
# Views
#
@urlpatterns.route('')
def home(request):
    ctx = {
        'conversations': Conversation.objects.all(),
        'home_banner_fragment': fragment('home.banner', raises=False),
        'how_it_works_fragment': fragment('home.how-it-works', raises=False),
        'start_now_fragment': fragment('home.start-now', raises=False),
        'social_media_icons': social_icons(),
    }
    return render(request, 'pages/home.jinja2', ctx)

@urlpatterns.route('conversations/create/')
def create_conversation(request):
    if request.user.id:
        form = ConversationForm()
        ctx = {'categories': Category.objects.all(), 'form': form}
        if request.method == 'GET':
            return render(request, 'pages/conversations-create.jinja2', ctx)
        elif request.method == 'POST':
            form = ConversationForm(data=request.POST, instance=Conversation(author=request.user))
            if form.is_valid():
                conversation = form.save()
                return redirect(f'/conversations/{conversation.category.slug}/{conversation.title}')
            else:
                print(form.errors)
                error_msg = _('Invalid conversation question or category')
                form.add_error(None, error_msg)
                ctx['form'] = form
                return render(request, 'pages/conversations-create.jinja2', ctx)
    return redirect('/login/')

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
