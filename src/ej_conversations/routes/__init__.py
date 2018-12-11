from boogie.router import Router
from ej_conversations import models

app_name = 'ej_conversations'
urlpatterns = Router(
    template=['ej_conversations/{name}.jinja2', 'generic.jinja2'],
    models={
        'conversation': models.Conversation,
        'comment': models.Comment,
    },
    lookup_field={
        'conversation': 'slug',
        'comment': 'slug',
    },
    lookup_type='slug',
)
conversation_url = f'<model:conversation>/'

# Must import after urlpatterns
from .admin import create, edit, get_conversation_moderate_context, get_conversation_edit_context, moderate
from .conversations import conversation_list, get_conversation_detail_context, detail
from .comments import comment_list, comment_detail
