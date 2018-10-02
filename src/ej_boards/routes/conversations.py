from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ej_conversations import forms
from ej_conversations.routes import conversation_detail_context, moderate_context, edit_context
from ej_clusters.routes import create_stereotype_context, edit_stereotype_context
from . import urlpatterns


@urlpatterns.route('<model:board>/conversations/', template='ej_conversations/list.jinja2')
def conversation_list(request, board):
    user = request.user
    conversations = board.conversations.all()
    board_user = board.owner
    boards = []
    boards_count = 0
    if user == board_user:
        boards = board_user.boards.all()
        boards_count = boards.count()
        user_is_owner = True
    else:
        user_is_owner = False
    return {
        'can_add_conversation': user_is_owner,
        'create_url': reverse('boards:create-conversation', kwargs={'board': board}),
        'conversations': conversations,
        'boards_count': boards_count,
        'boards': boards,
        'current_board': board,
        'is_a_board': True,
        'title': _("%s' conversations") % board.title,
        'subtitle': _("These are %s's conversations. Contribute to them too") % board.title,
    }


@urlpatterns.route('<model:board>/conversations/add/', perms=['ej_boards.can_add_conversation'])
def create_conversation(request, board):
    user = request.user
    form = forms.ConversationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            conversation = form.save_all(
                author=user,
                board=board,
            )
        return redirect(f'/{board.slug}/conversations/{conversation.slug}/stereotypes/')

    return {'form': form}


@urlpatterns.route('<model:board>/conversations/<model:conversation>/')
def conversation_detail(request, board, conversation):
    if conversation not in board.conversations.all():
        raise Http404
    return conversation_detail_context(request, conversation)


@urlpatterns.route('<model:board>/conversations/<model:conversation>/edit/', perms=['ej.can_edit_conversation'])
def edit_conversation(request, board, conversation):
    if conversation not in board.conversations.all():
        raise Http404
    return edit_context(request, conversation)


@urlpatterns.route('<model:board>/conversations/<model:conversation>/moderate/', perms=['ej.can_edit_conversation'])
def moderate_conversation(request, board, conversation):
    if conversation not in board.conversations.all():
        raise Http404
    return moderate_context(request, conversation, board)


@urlpatterns.route('<model:board>/conversations/<model:conversation>/stereotypes/',
                   perms=['ej.can_manage_stereotypes'])
def conversation_stereotype_list(request, board, conversation):
    return {
        'content_title': _('Stereotypes'),
        'conversation_title': conversation.title,
        'stereotypes': conversation.stereotypes.all(),
        'stereotype_url': conversation.get_absolute_url(board=board) + 'stereotypes/',
        'conversation_url': conversation.get_absolute_url(board=board),
    }


@urlpatterns.route('<model:board>/conversations/<model:conversation>/stereotypes/add/',
                   perms=['ej.can_manage_stereotypes'])
def create_conversation_stereotype(request, board, conversation):
    return create_stereotype_context(request, conversation, board)


@urlpatterns.route('<model:board>/conversations/<model:conversation>/stereotypes/<model:stereotype>/edit/',
                   perms=['ej.can_manage_stereotypes'])
def edit_conversation_stereotype(request, board, conversation, stereotype):
    return edit_stereotype_context(request, conversation, stereotype, board)
