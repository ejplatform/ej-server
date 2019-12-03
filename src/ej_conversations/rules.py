from random import randrange

from django.conf import settings
from django.utils.timezone import now

from boogie import rules
from .enums import Choice
from .models import Comment


#
# Global values and configurations
#
@rules.register_value("ej.max_comments_per_conversation")
def max_comments_per_conversation(conversation, user):
    """
    Limit the number of comments in a single conversation
    """
    DEFAULT_MAX_COMMENTS_PER_CONVERSATION = 2
    return getattr(settings, "EJ_MAX_COMMENTS_PER_CONVERSATION",
                   DEFAULT_MAX_COMMENTS_PER_CONVERSATION)


def comment_throttle():
    """
    Minimum interval between posts (in seconds).

    We avoid spam and bots by preventing users from posting too many comments
    or votes in a short time span.
    """
    DEFAULT_COMMENT_THROTTLE = 0
    return getattr(settings, "EJ_CONVERSATIONS_COMMENT_THROTTLE",
                   DEFAULT_COMMENT_THROTTLE)


def vote_throttle():
    """
    Minimum interval between votes (in seconds)
    """
    DEFAULT_VOTE_THROTTLE = 5
    return getattr(settings, "EJ_CONVERSATIONS_VOTE_THROTTLE",
                   DEFAULT_VOTE_THROTTLE)


@rules.predicate
def is_personal_conversations_enabled():
    """
    Check global config to see if personal conversations are allowed.
    """
    return getattr(settings, "EJ_ENABLE_BOARDS", True)


#
# Comments
#
@rules.register_value("ej.next_comment")
def next_comment(conversation, user):
    """
    Return a randomly selected comment for the user to vote.
    It will first choose a comment from promoted comments, then
    from user own non-voted comments and then the rest of the comments
    """
    if user.is_authenticated:
        # Non voted user-created comments
        non_voted_comments = conversation.approved_comments.filter(author=user).exclude(votes__author=user)
        size = non_voted_comments.count()
        if size:
            return non_voted_comments[randrange(0, size)]

        # Regular comments
        try:
            return conversation.approved_comments.exclude(votes__author=user).random()
        except Comment.DoesNotExist:
            pass

        # Comments the user has skip
        skipped_comments = conversation.approved_comments.filter(
            votes__author=user,
            votes__choice=Choice.SKIP)
        size = skipped_comments.count()
        if size:
            return skipped_comments[randrange(0, size)]
    return None


#
# Throttling and Limits
#
@rules.register_value("ej.remaining_comments")
def remaining_comments(conversation, user):
    """
    The number of comments user still have in a conversation.
    """
    if user is None or user.id is None:
        return 0

    fn_max_comments_per_conversation = rules.get_value(
        "ej.max_comments_per_conversation")
    max_num_comments = fn_max_comments_per_conversation(conversation, user)
    fallback_num_remaining_comments = 1 if user.has_perm(
        "ej.can_edit_conversation", conversation) else 0
    num_comments_made = user.comments.filter(conversation=conversation).count()
    return max(max_num_comments - num_comments_made,
               fallback_num_remaining_comments)


@rules.register_value("ej.comments_under_moderation")
def comments_under_moderation(conversation, user):
    """
    The number of comments under moderation of a user in a conversation.
    """
    if user.id is None:
        return 0
    return user.comments.filter(conversation=conversation,
                                status=Comment.STATUS.pending).count()


@rules.register_value("ej.comments_made")
def comments_made(conversation, user):
    """
    The number of comments made by user in a conversation
    """
    if user.id is None:
        return 0
    else:
        return user.comments.filter(conversation=conversation).count()


@rules.register_value("ej.vote_cooldown")
def vote_cooldown(conversation, user):
    """
    Number of seconds before user can vote again.
    """
    FALLBACK_INTERVAL_BETWEEN_VOTES = 0.0
    time_last_vote = (
        user.votes.filter(conversation=conversation)
        .order_by("created")
        .values_list("created", flat=True)
        .last()
    )
    if time_last_vote is None:
        return 0.0
    interval = now() - time_last_vote
    return max(vote_throttle() - interval.seconds,
               FALLBACK_INTERVAL_BETWEEN_VOTES)


#
# Permissions
#
@rules.register_perm("ej.can_vote")
def can_vote(user, conversation):
    """
    User can vote in a conversation if there are non-voted comments.
    """
    if user.id is None:
        return False
    return conversation.approved_comments.exclude(votes__author=user).exists()


@rules.register_perm("ej.can_comment")
def can_comment(user, conversation):
    """
    Check if user can comment in conversation.

    * User still has comments left
    * OR User is owner or can edit conversation
    """
    if user.id is None:
        return False
    if user.has_perm("ej.can_edit_conversation", conversation):
        return True
    num_remaining_comments = remaining_comments(conversation, user)
    return num_remaining_comments > 0


@rules.register_perm("ej.can_edit_conversation")
def can_edit_conversation(user, conversation):
    """
    Can edit a given conversation.

    * User is conversation author
    * OR Conversation is promoted and user can create/edit promoted conversations
    """
    if user.id == conversation.author_id:
        return True
    elif conversation.is_promoted and user.has_perm(
            "ej_conversations.can_publish_promoted"):
        return True
    return False


@rules.register_perm("ej.can_moderate_conversation")
def can_moderate_conversation(user, conversation):
    """
    Can moderate a given conversation.

    * User can edit conversation
    * OR user is an explict moderator (explicit permission)
    * OR user is an moderator in conversation
    """
    return (
        can_edit_conversation(user, conversation)
        or user.has_perm("ej_conversations.is_moderator")
        or user in conversation.moderators.all()
    )


@rules.register_perm("ej.can_promote_conversations")
def can_promote_conversation(user):
    """
    Check if user can add a promoted conversation

    * User is a publisher (explicit admin permission).
    """
    return user.has_perm("ej_conversations.can_publish_promoted")
