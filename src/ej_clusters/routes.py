from django.shortcuts import get_object_or_404

from boogie.router import Router
from ej_conversations.models import Category, Conversation
from .models import Stereotype, Cluster

urlpatterns = Router(
    template='ej_clusters/{name}.jinja2',
    base_url='<model:category>/<model:conversation>/',
    perms=['ej_converations.can_edit_conversation'],
    object='conversation',
    login=True,
    models={
        'category': Category,
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
def index(category, conversation):
    return {
        'category': category,
        'conversation': conversation,
    }


@urlpatterns.route('clusters/<int:index>/')
def detail(category, conversation, index):
    cluster = get_object_or_404(Cluster, conversation=conversation, index=index)
    return {
        'category': category,
        'conversation': conversation,
        'cluster': cluster,
    }


#
# Stereotypes
#
@urlpatterns.route('stereotypes/')
def stereotype_list(category, conversation):
    return {
        'category': category,
        'conversation': conversation,
        'stereotypes': conversation.stereotypes,
    }


@urlpatterns.route('stereotypes/<id>/')
def stereotype_vote(category, conversation, stereotype):
    return {
        'category': category,
        'conversation': conversation,
        'stereotype': stereotype,
        'comment': stereotype.next_comment(),
    }


@urlpatterns.post(...)
def stereotype_vote_post(category, conversation, stereotype):
    return {
        'category': category,
        'conversation': conversation,
        'stereotype': stereotype,
        'comment': stereotype.next_comment(),
    }
