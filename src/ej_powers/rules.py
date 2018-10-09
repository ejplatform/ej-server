from ej_powers.models import GivenPower
from ej_conversations.models import Conversation
from rules import predicate


@predicate
def is_opinion_bridge(user, conversation):
    """
    Return true if user has the "opinion bridge"
    """


@predicate
def can_be_opinion_link(user, conversation):
    """
    Opinion bridges sits between two clusters and may help to promote dialogue
    between both clusters.
    """


@predicate
def is_group_activist(user, conversation):
    pass


@predicate
def can_be_group_activist(user, conversation):
    pass


#
# Powers
#
@predicate
def can_promote_comment(user, conversation):
    return conversation in self_promote_set(user)


@predicate
def can_promote_self_comment(user, conversation):
    return conversation in self_promote_set(user)


def promote_set(user):
    """
    Return all conversations that user can promote a comment.
    """
    given_power_query = GivenPower.objects.filter(user=user).get_real_instances()
    if given_power_query:
        conversations = Conversation.objects.filter(givenpower__in=given_power_query)
    else:
        conversations = None
    return conversations


def self_promote_set(user):
    pass
