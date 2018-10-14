from boogie.router import Router
from ej_conversations.models import Conversation
from ej_boards.models import Board
from ej_clusters.models import Stereotype

app_name = 'ej_boards'

#
# Board management
#
urlpatterns = Router(
    template=['ej_boards/{name}.jinja2', 'generic.jinja2'],
    object='conversation',
    models={
        'board': Board,
        'conversation': Conversation,
        'stereotype': Stereotype,
    },
    lookup_field={'conversation': 'slug', 'board': 'slug'},
    lookup_type={'conversation': 'slug', 'board': 'slug'},
)

from .boards import list, create, edit
from .conversations import conversation_list, create_conversation, conversation_detail, edit_conversation, \
                            moderate_conversation, create_conversation_stereotype, edit_conversation_stereotype
