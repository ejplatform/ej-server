from django.urls import reverse

from boogie.router import Router
from ej_conversations import models
from ej_conversations.proxy import conversations_with_moderation
from .models import Board

app_name = 'ej_conversations'
urlpatterns = Router(
    template=['ej_conversations/{name}.jinja2', 'generic.jinja2'],
    models={
        'conversation': models.Conversation,
        'comment': models.Comment,
        'board': Board,
    },
    lookup_field='slug',
    lookup_type='slug',
    object='conversation',
)
board_url = '<model:board>/conversations/'


@urlpatterns.route(board_url, template='ej_conversations/list.jinja2')
def conversation_list(request, board):
    user = request.user
    conversations = board.conversations.all()
    return {
        'conversations': conversations_with_moderation(user, conversations),
        'can_add_conversation': user.has_perm('ej_conversations.can_add_conversation'),
        'create_url': reverse('boards:create', kwargs={'board': board})
    }


@urlpatterns.route(board_url + 'add/')
def create(request, board):
    return {
        'board': board,
    }


@urlpatterns.route(board_url + '<model:conversation>/')
def detail(request, board, conversation):
    return {
        'board': board,
        'conversation': conversation,
    }


@urlpatterns.route(board_url + '<model:conversation>/edit/')
def edit(request, board, conversation):
    return {
        'board': board,
        'conversation': conversation,
    }
