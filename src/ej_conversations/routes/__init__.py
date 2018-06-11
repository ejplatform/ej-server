from boogie.router import Router
from ej_conversations import models
from ej_users.models import User

app_name = 'ej_conversations'
urlpatterns = Router(
    template='ej_conversations/{name}.jinja2',
    models={
        'conversation': models.Conversation,
        'comment': models.Comment,
        'owner': User
    },
    lookup_field={
        'conversation': 'slug',
        'comment': 'slug',
        'owner': 'username',
    },
    lookup_type='slug',
    object='conversation',
)
base_url = 'conversations/'
conversation_url = f'{base_url}<model:conversation>/'
user_url = '<model:owner>/'

from .admin import create, edit, moderate
from .base import list, detail, info, leaderboard
from .comments import comment_list, comment_detail

