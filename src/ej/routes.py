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

@urlpatterns.route('conversation_create/')
@urlpatterns.route('conversation_edit/<id>')
def create_conversation(request, id=None):
    if request.user.id:
        form = ConversationForm()
        if request.method == 'GET':
            ctx = {
                'categories': Category.objects.all(),
                'conversation':  Conversation.objects.get(id=id) if id else Conversation(),
                'form': form,
            }
            return render(request, "pages/conversations-create.jinja2", ctx)
        elif request.method == 'POST':
            return save_or_update_conversation(request.POST, request.user, id)

    return redirect('/login/')

# @TODO move this method to a more generic module
def save_or_update_conversation(request_form, request_author, id):
    form = ConversationForm(data=request_form, instance=Conversation(author=request_author))
    
    if form.is_valid():
        if id:
            Conversation.objects.filter(id=id).update(
                question=form.cleaned_data['question'],
                title=form.cleaned_data['title'],
                category=form.cleaned_data['category'],
            )
            conversation = Conversation.objects.get(id=id)
        else:
            conversation = form.save()
            
        return redirect(f'/conversations/{conversation.category.slug}/{conversation.slug}')
    else:
        error_msg = _('Invalid conversation question or category')
        form.add_error(None, error_msg)
        ctx['form'] = form
        return render(request, 'pages/conversations-create.jinja2', ctx)
        

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
