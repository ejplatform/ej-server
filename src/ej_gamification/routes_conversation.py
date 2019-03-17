from boogie.router import Router

from ej_conversations.models import Conversation
from ej_conversations.utils import check_promoted
from ej_gamification import get_participation, get_progress

app_name = 'ej_gamification'
urlpatterns = Router(
    template='ej_gamification/conversation/{name}.jinja2',
    base_path='<model:conversation>/<slug:slug>/',
    models={
        'conversation': Conversation,
    },
    login=True,
)


@urlpatterns.route('achievements/')
def index(request, conversation, slug, check=check_promoted):
    check(conversation, request)
    user = request.user

    return {
        'user': user,
        'progress': get_participation(user, conversation),
        'conversation_progress': get_progress(conversation),
    }

