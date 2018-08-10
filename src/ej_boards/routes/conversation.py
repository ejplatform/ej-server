from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from boogie.router import Router
from ej_conversations.proxy import conversations_with_moderation
from ej_conversations import forms
from ..models import Board, BoardSubscription


app_name = 'ej_boards'
urlpatterns = Router(
    template=['ej_boards/{name}.jinja2', 'generic.jinja2'],
    models={
        'board': Board,
    },
    lookup_field='slug',
    lookup_type='slug',
)
board_url = '<model:board>/conversations/'


@urlpatterns.route(board_url, template='ej_conversations/list.jinja2')
def conversation_list(request, board):
    user = request.user
    conversations = board.conversations.all()
    tags = board.tags.all()
    return {
        'conversations': conversations_with_moderation(user, conversations),
        'categories': tags,
        'can_add_conversation': user.has_perm('ej_boards.can_add_conversation', board),
        'is_a_timeline': True,
        'is_my_timeline': user.has_perm('ej_boards.is_my_timeline', board),
        'create_url': reverse('board_conversation:create', kwargs={'board': board}),
        'title': _("%s' conversations") % board.title,
        'subtitle': _("These are %s's conversations. Contribute to them too") % board.title,
    }


@urlpatterns.route(board_url + 'add/', template='ej_conversations/create.jinja2')
def create(request, board):
    user = request.user
    form_class = forms.ConversationForm
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            conversation = form.save(commit=False)
            conversation.author = user
            conversation.save()

            BoardSubscription.objects.create(conversation=conversation, board=board)

            return redirect(conversation.get_absolute_url())
    else:
        form = form_class()

    return {
        'content_title': _('Create conversation'),
        'form': form,
    }
