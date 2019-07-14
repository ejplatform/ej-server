from django.dispatch import Signal, receiver

from ej_conversations.signals import vote_cast
from ej_gamification.models.progress import get_participation

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
@receiver(vote_cast)
def handle_vote(vote, comment, is_update, **kwargs):
    get_participation(vote.author, comment.conversation, sync=True)
