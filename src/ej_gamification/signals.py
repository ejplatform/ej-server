import random

from django.dispatch import Signal, receiver

from ej_conversations.signals import vote_cast, comment_moderated
from .models import get_participation, get_progress, UserProgress, ConversationProgress

UPDATE_PROBABILITY = 0.05

#
# Application signals
#
user_level_achieved = Signal(providing_args=["user", "level", "track", "is_improvement", "progress"])
conversation_level_achieved = Signal(
    providing_args=["conversation", "level", "track", "is_improvement", "progress"]
)
participation_level_achieved = Signal(
    providing_args=["user", "conversation", "level", "track", "is_improvement", "progress"]
)


#
# Handlers to external signals
#
def random_update(attr, func, *args, prob=UPDATE_PROBABILITY):
    if random.random() < prob:
        func(*args, sync=True)
    else:
        ctrl = func(*args, sync=False)
        if isinstance(attr, int):
            ctrl.score += attr
        else:
            ctrl.score += getattr(ctrl, attr + "_POINTS")
        ctrl.update_levels(commit=False)
        ctrl.save()


@receiver(vote_cast)
def handle_vote(vote, comment, is_final, **kwargs):
    # We accept small drifts in score values, and make a full update with a
    # small probability to optimize db access
    if is_final:
        author = vote.author
        conversation = comment.conversation

        score = UserProgress.VOTE_POINTS
        if vote.author_id == conversation.author_id:
            score += ConversationProgress.VOTE_POINTS

        random_update("VOTE", get_participation, author, conversation)
        random_update(score, get_progress, conversation)
        random_update("VOTE", get_progress, author)


@receiver(comment_moderated)
def handle_moderation(comment, author, **kwargs):
    if comment.is_pending:
        return
    elif comment.is_approved:
        status = "APPROVED_COMMENT"
    else:
        status = "REJECTED_COMMENT"

    conversation = comment.conversation
    random_update(status, get_participation, author, conversation)
    random_update(status, get_progress, author)
    random_update(status, get_progress, conversation)
