from django.shortcuts import get_object_or_404

from boogie.router import Router
from ej_conversations.models import Conversation
from .models import Stereotype, Cluster

urlpatterns = Router(
    template='ej_clusters/{name}.jinja2',
    base_url='<model:conversation>/',
    perms=['ej_converations.is_owner'],
    object='conversation',
    login=True,
    models={
        'conversation': Conversation,
        'stereotype': Stereotype,
    },
    lookup_field='slug',
    lookup_type='slug',
)


#
# Cluster info
#
@urlpatterns.route('clusters/')
def index(conversation):
    return {
        'conversation': conversation,
    }


@urlpatterns.route('clusters/<int:index>/')
def detail(conversation, index):
    cluster = get_object_or_404(Cluster, conversation=conversation, index=index)
    return {
        'conversation': conversation,
        'cluster': cluster,
    }


#
# Stereotypes
#
@urlpatterns.route('stereotypes/')
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
