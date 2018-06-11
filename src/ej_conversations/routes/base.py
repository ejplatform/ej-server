from django.http import HttpResponseServerError
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from boogie.rules import proxy_seq
from hyperpython import a
from . import urlpatterns, base_url, conversation_url, user_url
from .. import rules
from ..models import Conversation


@urlpatterns.route(base_url)
@urlpatterns.route(user_url + 'conversations/',
                   name='list-for-user',
                   template='ej_conversations/list.jinja2')
def list(request, owner=None):
    if owner:
        kwargs = {'owner': owner}
        create_url = reverse('conversations:create-for-user', kwargs=kwargs)
        conversations = Conversation.objects.filter(author=owner)
    else:
        create_url = reverse('conversations:create')
        conversations = Conversation.promoted.all()

    return {
        'conversations': moderated_conversations(request.user, conversations),
        'can_add_conversation': rules.can_add_conversation(request.user),
        'owner': owner,
        'add_link': a(_('Add new conversation'), href=create_url),
    }


@urlpatterns.route(user_url + conversation_url, name='detail-for-user')
@urlpatterns.route(conversation_url)
def detail(request, conversation, owner=None):
    comment = conversation.next_comment(request.user, None)
    ctx = {
        'conversation': conversation,
        'edit_perm': rules.can_edit_conversation(request.user, conversation),
        'comment': comment,
        'owner': owner,
    }
    if comment and request.POST.get('action') == 'vote':
        vote = request.POST['vote']
        if vote not in {'agree', 'skip', 'disagree'}:
            return HttpResponseServerError('invalid parameter')
        comment.vote(request.user, vote)
    elif request.POST.get('action') == 'comment':
        comment = request.POST['comment'].strip()
        try:
            ctx['comment'] = conversation.create_comment(request.user, comment)
        except PermissionError as ex:
            ctx['comment_error'] = str(ex)
    return ctx


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


def moderated_conversations(user, qs=None):
    perm = 'ej_conversations.can_moderate_conversation'
    kwargs = {
        'can_moderate': lambda x: user.has_perm(perm, x)
    }
    if qs is None:
        qs = Conversation.promoted.all()
    return proxy_seq(qs, user=user, **kwargs)
