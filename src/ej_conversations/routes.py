from django.http import HttpResponseServerError

from boogie.router import Router
from . import models

app_name = 'ej_conversations'
urlpatterns = Router(
    template='ej_conversations/{name}.jinja2',
    models={
        'conversation': models.Conversation,
        'comment': models.Comment,
    },
    lookup_field='slug',
    lookup_type='slug',
    object='conversation',
)
conversation_url = '<model:conversation>/'


@urlpatterns.route('')
def list():
    return {
        'conversations': models.Conversation.objects.all(),
    }


@urlpatterns.route(conversation_url)
def detail(request, conversation):
    comment = conversation.next_comment(request.user, None)
    ctx = {
        'conversation': conversation,
        'comment': comment,
    }
    if comment and request.POST.get('action') == 'vote':
        vote = request.POST['vote']
        if vote not in {'agree', 'skip', 'disagree'}:
            return HttpResponseServerError('invalid parameter')
        comment.vote(request.user, vote)
    elif request.POST.get('action') == 'comment':
        comment = request.POST['comment'].strip()
        conversation.create_comment(request.user, comment)
    return ctx


@urlpatterns.route('conversations/create/')
@urlpatterns.route('conversations/edit/<id>')
def create_or_update(request, id=None):
    if request.user.id:
        form = ConversationForm()
        if request.method == 'GET':
            ctx = {
                'categories': Category.objects.all(),
                'conversation': Conversation.objects.get(id=id) if id else Conversation(),
                'form': form,
            }
            return render(request, "pages/conversations-create.jinja2", ctx)
        elif request.method == 'POST':
            return save_or_update_conversation(request.POST, request.user, id)

    return redirect('/login/')


@urlpatterns.route(conversation_url + 'comments/')
def comment_list(conversation):
    return {
        'conversation': conversation,
        'comments': conversation.comments.all(),
    }


@urlpatterns.route(conversation_url + 'comments/<model:comment>/', lookup_field={'comment': 'pk'})
def comment_detail(conversation, comment):
    return {
        'conversation': conversation,
        'comment': comment,
    }


@urlpatterns.route(conversation_url + 'info/')
def info(conversation):
    return {
        'conversation': conversation,
        'info': conversation.statistics(),
    }


@urlpatterns.route(conversation_url + 'leaderboard/')
def leaderboard(conversation):
    return {
        'conversation': conversation,
        'info': conversation.statistics(),
    }


#
# Administrative views
#
@urlpatterns.route('add/',
                   template=True,
                   perms=['ej_conversations.can_add_conversation'])
def create_conversation():
    return {
        'form': None,
    }


@urlpatterns.route(conversation_url + 'edit/',
                   perms=['ej_conversations.can_edit_conversation'],
                   template=True)
def edit_conversation(conversation):
    return {
        'conversation': conversation,
    }


@urlpatterns.route(conversation_url + 'moderate/',
                   perms=['ej_conversations.can_edit_conversation'],
                   template=True)
def moderate_comments(conversation):
    return {
        'conversation': conversation,
        'comments': conversation.comments.pending(),
    }


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