from boogie.router import Router
from ej_conversations.models import Category, Conversation

urlpatterns = Router(
    template='ej_reports/{name}.jinja2',
    base_url='<slug@slug:category>/<slug@slug:conversation>/',
    perms=['ej_reports.can_view_report'],
    object='conversation',
    login=True,
)


@urlpatterns.route(template=True)
def index(category: Category, conversation: Conversation):
    return {
        'category': category,
        'conversation': conversation,
    }


@urlpatterns.route('clusters/', template=True)
def clusters(category: Category, conversation: Conversation):
    return {
        'category': category,
        'conversation': conversation,
    }


@urlpatterns.route('radar/', template=True)
def radar(category: Category, conversation: Conversation):
    return {
        'category': category,
        'conversation': conversation,
    }


@urlpatterns.route('divergence/', template=True)
def divergence(category: Category, conversation: Conversation):
    return {
        'category': category,
        'conversation': conversation,
    }
