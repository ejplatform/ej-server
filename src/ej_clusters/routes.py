from django.shortcuts import get_object_or_404

from boogie.router import Router
from ej_conversations.models import Conversation
from .models import Stereotype, Cluster

urlpatterns = Router(
    template='ej_clusters/{name}.jinja2',
    perms=['ej_converations.can_edit_conversation'],
    object='conversation',
    login=True,
    models={
        'conversation': Conversation,
        'stereotype': Stereotype,
    },
    lookup_field='slug',
    lookup_type='slug',
)
conversation_url = '<model:conversation>/'


#
# Cluster info
#
@urlpatterns.route(conversation_url + 'clusters/')
def index(conversation):
    return {
        'conversation': conversation,
    }


@urlpatterns.route(conversation_url + 'clusters/<int:index>/')
def detail(conversation, index):
    cluster = get_object_or_404(Cluster, conversation=conversation, index=index)
    return {
        'conversation': conversation,
        'cluster': cluster,
    }


#
# Stereotypes
#
@urlpatterns.route(conversation_url + 'stereotypes/')
def stereotype_list(conversation):
    return {
        'conversation': conversation,
        'stereotypes': conversation.stereotypes,
    }


@urlpatterns.route('stereotypes/<id>/')
def stereotype_vote(conversation, stereotype):
    return {
        'conversation': conversation,
        'stereotype': stereotype,
        'comment': stereotype.next_comment(),
    }


@urlpatterns.post(...)
def stereotype_vote_post(conversation, stereotype):
    return {
        'conversation': conversation,
        'stereotype': stereotype,
        'comment': stereotype.next_comment(),
    }
