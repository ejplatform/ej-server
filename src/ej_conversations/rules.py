from random import randrange

from django.conf import settings
from django.db.models import Q
from django.utils.timezone import now

from boogie import rules
from ej_users.models import User
from ej_conversations.models import Conversation


#
# Global values and configurations
#
def max_comments_per_conversation():
    """
    Limit the number of comments in a single conversation
    """
    return getattr(settings, 'EJ_CONVERSATIONS_MAX_COMMENTS', 2)


def comment_throttle():
    """
    Minimum interval between posts (in seconds).

    We avoid spam and bots by preventing users from posting too many comments
    or votes in a short time span.
    """
    return getattr(settings, 'EJ_CONVERSATIONS_COMMENT_THROTTLE', 0)


def vote_throttle():
    """
    Minimum interval between votes (in seconds)
    """
    return getattr(settings, 'EJ_CONVERSATIONS_VOTE_THROTTLE', 5)


@rules.predicate
def is_personal_conversations_enabled():
    """
    Check global config to see if personal conversations are allowed.
    """
    return getattr(settings, 'EJ_CONVERSATIONS_ALLOW_PERSONAL_CONVERSATIONS', True)


#
# Conversations
#
@rules.register_rule('ej_conversations.has_conversation')
def has_conversation(user):
    """
    Verify if a user has any conversation.
    """
    if Conversation.objects.filter(author=user).count() > 0:
        return True
    else:
        return False


#
# Comments
#
@rules.register_value('ej_conversations.next_comment')
def next_comment(conversation, user):
    """
    Return a randomly selected comment for the user to vote.
    """
    unvoted_comments = conversation.approved_comments.filter(
        ~Q(author_id=user.id),
        ~Q(votes__author_id=user.id),
    )
    size = unvoted_comments.count()
    if size:
        return unvoted_comments[randrange(0, size)]
    else:
        return None


#
# Throttling and Limits
#
@rules.register_value('ej_conversations.remaining_comments')
def remaining_comments(conversation, user):
    """
    The number of comments user still have in a conversation.
    """
    if user.id is None:
        return 0
    comments = user.comments.filter(conversation=conversation).count()
    return max(max_comments_per_conversation() - comments, 0)


@rules.register_value('ej_conversations.vote_cooldown')
def vote_cooldown(conversation, user):
    """
    Number of seconds before user can vote again.
    """
    time = (
        user.votes
            .filter(conversation=conversation)
            .order_by('created')
            .values_list('created', flat=True)
            .last()
    )
    if time is None:
        return 0.0
    interval = now() - time
    return max(vote_throttle() - interval.seconds, 0.0)


#
# Permissions
#
@rules.register_perm('ej_conversations.can_vote')
def can_vote(user, conversation):
    """
    User can vote in a conversation if there are unvoted comments.
    """
    if user.id is None:
        return False
    return bool(
        conversation.approved_comments
            .exclude(votes__author_id=user.id)
    )


@rules.register_perm('ej_conversations.can_comment')
def can_comment(user, conversation):
    """
    Check if user can comment in conversation.

    * User still has comments left
    * OR User is owner or can edit conversation
    """
    if user.id is None:
        return False
    if user.has_perm('ej_conversations.can_edit_conversation'):
        return True
    remaining = remaining_comments(conversation, user)
    return remaining > 0


# @TODO create a logic to create conversation permission
@rules.register_perm('ej_conversations.can_add_conversation')
def can_add_conversation(user):
    if User.objects.filter(username=user.username).exists():
        return True
    return False


@rules.register_perm('ej_conversations.can_edit_conversation')
def can_edit_conversation(user, conversation):
    """
    Can edit a given conversation.

    * User is conversation author
    * OR Conversation is promoted and user can create/edit promoted conversations
    """
    if conversation is None:
        return False
    elif user == conversation.author:
        return True
    elif (conversation.status == conversation.STATUS.promoted
          and user.has_perm('ej_conversations.can_publish')):
        return True
    return False


@rules.register_perm('ej_conversations.can_moderate_conversation')
def can_moderate_conversation(user, conversation):
    """
    Can moderate a given conversation.

    * User can edit conversation
    * OR user is an moderator (explicit admin permission)
    """
    return (
        can_edit_conversation(user, conversation)
        or user.has_perm('ej_conversations.can_moderate')
    )
