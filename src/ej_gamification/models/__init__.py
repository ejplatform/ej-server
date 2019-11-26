from .endorsement import Endorsement, endorse_comment, is_endorsed
from .given_powers import GivenBridgePower, GivenMinorityPower, GivenPower
from .progress_base import get_participation, get_progress
from .progress_conversation import ConversationProgress
from .progress_participation import ParticipationProgress
from .progress_user import UserProgress

# ------------------------------------------------------------------------------
# Patch models
# ------------------------------------------------------------------------------
__run = lambda: lambda f: f()


@__run()
def _patch_models():
    """
    Patch external models with gamification properties.
    """
    from django.db.models import Sum
    from django.contrib.auth import get_user_model
    from sidekick import lazy

    user = get_user_model()

    def patch(model, how=lambda x: x):
        def patcher(func):
            setattr(model, func.__name__, how(func))
            return func

        return patcher

    #
    # Patch user model with progress tracks
    #
    @patch(user, lazy)
    def total_conversation_score(user):
        agg = user.conversations.aggregate(r=Sum("progress__score"))
        return agg["r"] or 0

    @patch(user, lazy)
    def total_participation_score(user):
        agg = user.participation_progresses.aggregate(r=Sum("score"))
        return agg["r"] or 0

    # @patch(user, lazy)
    # def n_trophies(user):
    #     return user.progress.n_trophies

    # FIXME: gamification
    user.n_endorsements = 0
    user.n_given_opinion_bridge_powers = 0
    user.n_given_minority_activist_powers = 0

    #
    # Patch comment
    #

    # Return a no-op function, if someone wants to call us again
    return lambda: None
