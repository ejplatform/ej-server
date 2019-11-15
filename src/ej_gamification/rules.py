from datetime import timedelta

from boogie.rules.valuemap import default_value_map
from django.conf import settings
from django.utils import timezone
from rules import predicate
from ej_conversations.rules import max_comments_per_conversation as _max_comments_per_conversation

from . import models, get_participation

# from .models import GivenBridgePower
POWER_ROLE_CONFIGURATION_MAP = {
    "endorsement": ("EJ_GAMIFICATION_ENDORSEMENT_DURATION", 14 * 24),
    "bridge-power": ("EJ_GAMIFICATION_BRIDGE_POWER_DURATION", 7 * 24),
    "minority-power": ("EJ_GAMIFICATION_MINORITY_POWER_DURATION", 7 * 24),
}

#
# Global configurations
#

def power_expiration_time(role, start=None):
    """
    Return the default expiration time for endorsements created in the given
    time.

    Args:
        role (str):
            Describes the power referring to the expiration duration.
            One of 'endorsement', 'bridge-power' or 'minority-power'
        start (datetime):
            If given, marks the date in which the power started. In defaults to
            the current datetime, but can be any date in the past or future.
    """
    start = start or timezone.now()
    role_variable, default = POWER_ROLE_CONFIGURATION_MAP[role]
    duration = getattr(settings, role_variable, default)
    duration *= 60 * 60
    return start + timedelta(seconds=duration)


#
# Override other EJ rules
#

def max_comments_per_conversation(conversation, user):
    """
    Limit the number of comments in a single conversation
    """
    default = _max_comments_per_conversation(conversation, user)
    extra = 0
    if conversation.author_id != getattr(user, "id", None):
        extra = get_participation(user, conversation).voter_level.comment_bonus
    return default + extra


default_value_map["ej.max_comments_per_conversation"] = max_comments_per_conversation


#
# Permissions and predicates
#

"""
The two functions bellow have the following behaviour:

has_opinion_bridge_power(function) = True if user is a "opinion bridge" in conversation.
has_activist_power(function) = True if the user has "activist" status in conversation.

"""

@predicate
def has_opinion_bridge_power(user, conversation):
    return models.GivenBridgePower.objects.filter(user=user, conversation=conversation).exists()


@predicate
def has_activist_power(user, conversation):
    return models.GivenMinorityPower.objects.filter(user=user, conversation=conversation).exists()

