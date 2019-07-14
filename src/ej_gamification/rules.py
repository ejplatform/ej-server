from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rules import predicate
from . import models

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
    variable_name, default = POWER_ROLE_CONFIGURATION_MAP[role]
    duration = getattr(settings, variable_name, default)
    duration *= 60 * 60
    return start + timedelta(seconds=duration)


#
# Permissions and predicates
#
@predicate
def has_opinion_bridge_power(user, conversation):
    """
    Return true if user is a "opinion bridge" in conversation.
    """
    return models.GivenBridgePower.objects.filter(user=user, conversation=conversation).exists()


@predicate
def can_be_opinion_bridge(user, conversation):
    """
    Opinion bridges sits between two clusters and may help to promote dialogue
    between both clusters.
    """


@predicate
def has_activist_power(user, conversation):
    return models.GivenMinorityPower.objects.filter(user=user, conversation=conversation).exists()


@predicate
def can_be_activist(user, conversation):
    """
    Activist is someone that is in a cluster and agrees with most opinions, but
    has some divergent opinion
    """
    pass
