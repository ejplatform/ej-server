from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from boogie import rules
from hyperpython import a
from . import urlpatterns, conversation_url
from ..models import FavoriteConversation, Conversation


@urlpatterns.route('', name='list')
def conversation_list(request):
    return {
        'conversations': Conversation.objects.filter(is_promoted=True),
        # FIXME: disable until form can register new conversation
        'can_add_conversation': False,  # request.user.has_perm('ej.can_add_promoted_conversation'),
        'create_url': reverse('conversation:create'),
        'topic': _("A space for adolescents to discuss actions that promote, guarantee and defend their rights"),
        'title': _("Public conversations"),
        'subtitle': _("Participate of the conversations and give your opinion with comments and votes!"),
        'footer_content': {
            'image': '/static/img/icons/facebook-blue.svg',
            'first': {'normal': 'Plataforma desenvolvida pelo', 'bold': 'Conanda/MDH/UnB'},
            'last': {'normal': 'Para denunciar:', 'bold': 'Disque 100 e #HUMANIZAREDES'}
        }
    }


@urlpatterns.route(conversation_url)
def detail(request, conversation, owner=None):
    user = request.user
    comment = conversation.next_comment(user, None)
    favorites = FavoriteConversation.objects.filter(conversation=conversation)
    ctx = {
        'conversation': conversation,
        'comment': comment,
        'owner': owner,
        'edit_perm': user.has_perm('ej_conversations.can_edit_conversation', conversation),
        'login_link': a(_('login'), href=reverse('auth:login') + '?next=' + conversation.get_absolute_url()),
        'favorites': favorites,
    }

    if comment and request.POST.get('action') == 'vote':
        vote = request.POST['vote']
        if vote not in {'agree', 'skip', 'disagree'}:
            return HttpResponseServerError('invalid parameter')
        comment.vote(user, vote)

    elif request.POST.get('action') == 'comment':
        comment = request.POST['comment'].strip()

        # FIXME: do not hardcode this and use a proper form!
        comment = comment[:210]
        try:
            ctx['comment'] = conversation.create_comment(user, comment)
        except (PermissionError, ValidationError) as ex:
            ctx['comment_error'] = str(ex)
            print(str(ex))
    elif request.POST.get('action') == 'favorite':
        conversation.toggle_favorite(user)

    ctx['can_comment'] = user.has_perm('ej_conversations.can_comment', conversation)
    ctx['remaining_comments'] = rules.compute('ej_conversations.remaining_comments', conversation, user)
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
