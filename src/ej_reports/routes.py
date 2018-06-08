from boogie.router import Router
from ej_conversations.models import Conversation


app_name = 'ej_reports'
urlpatterns = Router(
    template='ej_reports/{name}.jinja2',
    perms=['ej_reports.can_view_report'],
    object='conversation',
    models={
        'conversation': Conversation,
    },
    lookup_field='slug',
    lookup_type='slug',
    login=True,
)
conversation_url = '<model:conversation>/reports/'


@urlpatterns.route(conversation_url)
def index(conversation):
    return {
        'conversation': conversation,
    }


@urlpatterns.route(conversation_url + 'clusters/')
def clusters(conversation):
    return {
        'conversation': conversation,
    }


@urlpatterns.route(conversation_url + 'radar/')
def radar(conversation):
    return {
        'conversation': conversation,
    }


@urlpatterns.route(conversation_url + 'divergence/')
def divergence(conversation):
    return {
        'conversation': conversation,
    }
