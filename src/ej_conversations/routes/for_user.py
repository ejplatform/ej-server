from django.contrib.auth import get_user_model
from django.http import Http404

from boogie.router import Router
from .. import models
from .. import routes

app_name = 'ej_conversations'
urlpatterns = Router(
    template=['ej_conversations/{name}.jinja2', 'generic.jinja2'],
    models={
        'conversation': models.Conversation,
        'comment': models.Comment,
        'owner': get_user_model(),
    },
    lookup_field={
        'conversation': 'slug',
        'comment': 'slug',
        'owner': 'board_name',
    },
    lookup_type='slug',
    object='conversation',
)
base_url = 'conversations/'
board_url = '<model:owner>/'

@urlpatterns.route(board_url, name='list')
def conversation_list(request, owner):
    return routes.conversation_list(request, owner)


@urlpatterns.route(base_url + 'add/')
def create(request):
    #if request.user != owner:
        #raise Http404
    return routes.create(request)


@urlpatterns.route(base_url + '<model:conversation>/')
def detail(request, conversation, owner):
    return routes.detail(request, conversation, owner)


@urlpatterns.route(base_url + '<model:conversation>/edit/')
def edit(request, conversation, owner):
    if request.user != owner:
        raise Http404
    return routes.edit(request, conversation, owner)
