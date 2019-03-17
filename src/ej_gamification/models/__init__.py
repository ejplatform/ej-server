# from .endorsement import Endorsement
# from .given_powers import GivenBridgePower, GivenMinorityPower, GivenPower

from .progress import UserProgress, ConversationProgress, ParticipationProgress

# from sidekick import call as _call
_call = lambda: lambda f: f()


@_call()
def _patch_user():
    """
    Patch user model with gamification properties.
    """
    from django.db.models import Sum
    from django.contrib.auth import get_user_model
    from sidekick import lazy

    model = get_user_model()

    def patch(func):
        setattr(model, func.__name__, lazy(func))
        return func

    #
    # Progress tracks
    #
    @patch
    def total_conversation_score(user):
        agg = user.conversations.aggregate(r=Sum('progress__score'))
        return agg['r'] or 0

    @patch
    def total_participation_score(user):
        agg = user.participation_progresses.aggregate(r=Sum('score'))
        return agg['r'] or 0

    model.n_endorsements = 0
    model.n_given_opinion_bridge_powers = 0
    model.n_given_minority_activist_powers = 0
    return None
