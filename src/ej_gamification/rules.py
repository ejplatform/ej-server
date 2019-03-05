from django.contrib.auth.models import AnonymousUser
from ej_conversations.models import Conversation, Comment
from rules import predicate
from .models import GivenPower, CommentPromotion, GivenBridgePower, GivenMinorityPower


@predicate
def has_opinion_bridge_power(user, conversation):
    """
    Return true if user has the "opinion bridge"
    """
    return GivenBridgePower.objects.filter(user=user, conversation=conversation).exists()


@predicate
def can_be_opinion_bridge(user, conversation):
    """
    Opinion bridges sits between two clusters and may help to promote dialogue
    between both clusters.
    """


@predicate
def has_activist_power(user, conversation):
    return GivenMinorityPower.objects.filter(user=user, conversation=conversation).exists()


@predicate
def can_be_activist(user, conversation):
    """
    Activist is someone that is in a cluster and agrees with most opinions, but
    has some divergent opinion
    """
    pass


#
# Powers
#
@predicate
def can_promote_comment(user, conversation):
    return conversation in promote_set(user)


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


def promoted_comments_in_conversation(user, conversation):
    """
    Return all comments promoted in a conversation for a user
    """
    if not isinstance(user, AnonymousUser):
        comment_promotions = CommentPromotion.objects.filter(comment__conversation=conversation, users=user)
        comments = Comment.objects.filter(commentpromotion__in=comment_promotions)
        return comments
    else:
        return Comment.objects.none()
