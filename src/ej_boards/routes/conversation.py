from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from boogie.router import Router
from ej_conversations import forms
from ej_conversations.proxy import conversations_with_moderation
from ..models import Board

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
    board_user = board.owner
    boards = []
    if user == board_user:
        boards = board_user.boards.all()

    return {
        'conversations': conversations_with_moderation(user, conversations),
        'boards': boards,
        'current_board': board,
        'can_add_conversation': board_user == user,
        'is_a_board': True,
        'owns_board': user == board.owner,
        'create_url': reverse('board_conversation:create', kwargs={'board': board}),
        'title': _("%s' conversations") % board.title,
        'subtitle': _("These are %s's conversations. Contribute to them too") % board.title,
    }


@urlpatterns.route(board_url + 'add/', template='ej_conversations/create.jinja2')
def create(request, board):
    user = request.user
    if not user.has_perm('ej_boards.can_add_conversation', board):
        raise PermissionError

    form = forms.ConversationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            conversation = form.save_all(
                author=user,
                board=board,
            )
        return redirect(f'/{board.slug}/conversations/{conversation.slug}')

    return {'form': form}
