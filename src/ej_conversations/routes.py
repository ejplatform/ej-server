from django.http import HttpResponseServerError, Http404
from django.shortcuts import redirect

from boogie.router import Router
from . import models, forms
from . import rules
from django.shortcuts import render
from ej_users.models import User
from ej.utils.perms import conversations

app_name = 'ej_conversations'
urlpatterns = Router(
    template='ej_conversations/{name}.jinja2',
    models={
        'conversation': models.Conversation,
        'comment': models.Comment,
        'user': User
    },
    lookup_field={
        'conversation': 'slug',
        'comment': 'slug',
        'user': 'username',
    },
    lookup_type='slug',
    object='conversation',
)
conversation_url = '<model:conversation>/'
base_url = 'conversations/'
user_url = '<model:user>/'


#
# Administrative views
#
@urlpatterns.route(base_url + 'add/',
                   perms=['ej_conversations.can_add_conversation'])
def create(request):
    if request.method == 'GET':
        return {
            'form': forms.ConversationForm(),
        }
    elif request.method == 'POST':
        form = forms.ConversationForm(
            data=request.POST,
            instance=models.Conversation(author=request.user),
        )
        if form.is_valid():
            conversation = form.save()
            return redirect(conversation.get_absolute_url())


@urlpatterns.route(base_url + conversation_url + 'edit/')
def edit(request, conversation):
    if not request.user.has_perm('ej_conversations.can_edit_conversation', conversation):
        raise Http404

    if request.method == 'GET':
        return {
            'form': forms.ConversationForm(instance=conversation)
        }
    elif request.method == 'POST':
        form = forms.ConversationForm(
            data=request.POST,
            instance=conversation,
        )
        if form.is_valid():
            form.instance.save()
        return redirect(conversation.get_absolute_url())


@urlpatterns.route(base_url + conversation_url + 'moderate/')
def moderate(request, conversation):
    if not request.user.has_perm('ej_conversations.can_moderate_conversation', conversation):
        raise Http404
            
    comments = []
    if request.method == 'POST':
        comment = models.Comment.objects.get(id=request.POST['comment'])
        comment.status = comment.STATUS.approved if request.POST['vote'] == 'approve' else comment.STATUS.rejected
        comment.save()

    # GET and Pos-Post
    for comment in models.Comment.objects.filter(conversation=conversation, status='pending'):
        if(comment.is_pending):
            comments.append(comment)
    return {
        'conversation': conversation,
        'comments': comments,
    }


@urlpatterns.route(base_url)
def list(request):
    return {
        'conversations': conversations(
            request.user,
            [rules.can_moderate_conversation]
        ),
        'add_conversation_perm': rules.can_add_conversation(request.user),

    }

@urlpatterns.route(user_url +"conversations/"+ conversation_url)
@urlpatterns.route(base_url + conversation_url)
def detail(request, conversation, user=None):
    comment = conversation.next_comment(request.user, None)
    ctx = {
        'conversation': conversation,
        'edit_perm': rules.can_edit_conversation(request.user, conversation),
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


@urlpatterns.route(base_url + conversation_url + 'comments/')
def comment_list(conversation):
    return {
        'conversation': conversation,
        'comments': conversation.comments.all(),
    }


@urlpatterns.route(base_url + conversation_url + 'comments/<model:comment>/', lookup_field={'comment': 'pk'})
def comment_detail(conversation, comment):
    return {
        'conversation': conversation,
        'comment': comment,
    }


@urlpatterns.route(base_url + conversation_url + 'info/')
def info(conversation):
    return {
        'conversation': conversation,
        'info': conversation.statistics(),
    }


@urlpatterns.route(base_url + conversation_url + 'leaderboard/')
def leaderboard(conversation):
    return {
        'conversation': conversation,
        'info': conversation.statistics(),
    }
