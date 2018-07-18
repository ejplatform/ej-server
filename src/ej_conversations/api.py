from boogie.rest import rest_api
from ej_clusters.math import get_raw_votes
from ej_conversations.models import Conversation


#
# Conversation extra actions and attributes
#
@rest_api.action('ej_conversations.Conversation')
def vote_dataset(request, conversation):
    df = get_raw_votes(conversation)
    return df.to_dict(orient='list')


@rest_api.action('ej_conversations.Conversation')
def user_statistics(request, conversation):
    return conversation.user_statistics(request.user)


@rest_api.action('ej_conversations.Conversation')
def approved_comments(conversation):
    return conversation.comments.approved()


@rest_api.action('ej_conversations.Conversation')
def random_comment(request, conversation):
    return conversation.next_comment(request.user)


@rest_api.action('ej_conversations.Conversation', list=True)
def random(request):
    return Conversation.objects.random(request.user)


@rest_api.property('ej_conversations.Conversation')
def statistics(conversation):
    return conversation.statistics()
