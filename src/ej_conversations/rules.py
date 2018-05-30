from random import randrange

from django.conf import settings
from django.db.models import Q
from django.utils.timezone import now

from boogie import rules


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
    return getattr(settings, 'EJ_CONVERSATIONS_COMMENT_THROTTLE', 2 * 60)


def vote_throttle():
    """
    Minimum interval between votes (in seconds)
    """
    return getattr(settings, 'EJ_CONVERSATIONS_VOTE_THROTTLE', 10)


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


@rules.register_value('ej_conversations.comment_cooldown')
def comment_cooldown(conversation, user):
    """
    Number of seconds before user can comment again.
    """
    time = (
        user.comments
            .filter(conversation=conversation)
            .order_by('created')
            .values_list('created', flat=True)
            .last()
    )
    if time is None:
        return 0.0
    print('rules', now() - time, comment_throttle())
    interval = now() - time
    return max(comment_throttle() - interval.seconds, 0.0)


#
# Permissions
#
@rules.register_perm('ej_conversations.can_vote')
def can_vote(user, conversation):
    """
    User can vote in a conversation if there are unvoted comments.
    """
    return bool(conversation.approved_comments.filter(
        ~Q(author_id=user.id),
        ~Q(votes__author_id=user.id),
    ))


@rules.register_perm('ej_conversations.can_comment')
def can_comment(user, conversation):
    """
    User can vote in a conversation if the limit of comments
    """
    remaining = remaining_comments(conversation, user)
    return remaining > 0 and comment_cooldown(conversation, user) <= 0.0


#@TODO create a logic to create conversation permission
@rules.register_perm('ej_conversations.can_add_conversation')
def can_add_conversation(user):
    return True


#@TODO create a logic to edit conversation permission
@rules.register_perm('ej_conversations.can_edit_conversation')
def can_edit_conversation(user, conversation):
    return user == conversation.author


@rules.predicate
def is_publisher(user):
    return False


rules.add_perm('ej_conversations.can_create_promoted_conversation',
               is_publisher | rules.is_staff | rules.is_superuser)
