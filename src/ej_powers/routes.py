from boogie.router import Router
from django.utils.translation import ugettext_lazy as _
from django.http import Http404

from ej_boards.routes import assure_correct_board
from ej_boards.models import Board
from ej_conversations.models import Conversation, Comment
from ej_conversations.forms import CommentForm
from ej_powers.rules import can_promote_comment

conversation_url = f'conversations/<model:conversation>/'
app_name = 'ej_powers'
urlpatterns = Router(
    template=['ej_powers/{name}.jinja2', 'generic.jinja2'],
    login=True,
    models={
        'conversation': Conversation,
        'board': Board,
    },
    lookup_field={'conversation': 'slug', 'board': 'slug'},
    lookup_type={'conversation': 'slug', 'board': 'slug'},
)


@urlpatterns.route(conversation_url + 'promote/')
def conversation_promote(request, conversation):
    if conversation.is_promoted:
        return conversation_promote_context(request, conversation)
    else:
        raise Http404


@urlpatterns.route('<model:board>/' + conversation_url + 'promote/', template='ej_powers/conversation-promote.jinja2')
def board_conversation_promote(request, board, conversation):
    assure_correct_board(conversation, board)
    return conversation_promote_context(request, conversation)


# Auxiliar function
def conversation_promote_context(request, conversation):
    if can_promote_comment(request.user, conversation):
        comment_form = CommentForm(request.POST or None, conversation=conversation)
        return{
            'comments': Comment.objects.filter(conversation=conversation),
            'conversations': conversation,
            'comment_form': comment_form,
            'title': _('My Comments'),
            'form_title': _('Comment and Promote')

        }
    else:
        raise Http404
