from boogie.router import Router
from ej_conversations.models import Conversation
from ej_boards.models import Board

app_name = 'ej_boards'

#
# Board management
#
urlpatterns = Router(
    template=['ej_boards/{name}.jinja2', 'generic.jinja2'],
    models={
        'board': Board,
        'conversation': Conversation,
    },
    object='conversation',
    lookup_field='slug',
    lookup_type='slug',
)


from .boards import list, create, edit
from .conversations import conversation_list, create_conversation, conversation_detail, edit_conversation, moderate_conversation
