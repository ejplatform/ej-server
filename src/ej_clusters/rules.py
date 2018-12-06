import logging

from django.db.models import Count

from boogie import rules
from ej_conversations.models import Conversation
from . import models, ClusterStatus

log = logging.getLogger('ej')

VOTES_FOR_USER_TO_PARTICIPATE_IN_CLUSTERIZATION = 5
VOTES_FOR_COMMENT_TO_PARTICIPATE_IN_CLUSTERIZATION = 5
MINIMUM_NUMBER_OF_CLUSTERS = 2


#
# Conversation permissions
#
@rules.register_rule('ej.must_update_clusterization')
def must_update_clusterization(obj):
    """
    Check if it requires a full re-clusterization.

    * Must have a defined clusterization
    * IF clusterization has status=PENDING, it must:
        - test OK for the 'ej.can_activate_clusterization' rule
    * In either case, it must:
        - Have the minimum number of clusters
        - Have not been clusterized sooner than TIMESTAMP - COOLDOWN_TIME
        - Have at least A unprocessed votes from active users
        - (or) Has at least C unprocessed comments with V or more votes

    A = VOTES_FOR_USER_TO_PARTICIPATE_IN_CLUSTERIZATION
    B =
    C =
    Argument must be a conversation or a clusterization.
    """
    clusterization = get_clusterization(obj)
    if clusterization is None:
        return False

    return (
        clusterization.unprocessed_votes >= 5
        or clusterization.unprocessed_comments >= 1
    )


@rules.register_rule('ej.can_activate_clusterization')
def can_activate_clusterization(obj):
    """
    Check if conversation/clusterization has sufficient data to start
    clusterization job.

    * Must have a defined clusterization
    * Has at least 5 comments with at least 5 votes.
    * Has at least 2 clusters with at least 1 registered stereotype.
    """
    clusterization = get_clusterization(obj)
    if clusterization is None:
        return False

    filled_comments = \
        (clusterization.comments
            .annotate(count=Count('votes'))
            .filter(count__gte=5)
            .count())
    filled_clusters = \
        (clusterization.clusters
            .annotate(count=Count('stereotypes'))
            .filter(count__gte=2)
            .count())
    return filled_comments >= 5 and filled_clusters >= 2


def requires_update(self):
    """
    Check if update should be recomputed.
    """
    conversation = self.conversation
    if self.cluster_status == ClusterStatus.PENDING_DATA:
        rule = rules.get_rule('ej.conversation_can_start_clusterization')
        if not rule.test(self):
            log.info(f'[clusters] {conversation}: not enough data to start clusterization')
            return False
    elif self.cluster_status == ClusterStatus.DISABLED:
        return False

    rule = rules.get_rule('ej.conversation_must_update_clusters')
    return rule.test(conversation)


@rules.register_perm('ej.can_be_clusterized')
def can_be_clusterized(user, conversation):
    """
    Check if user can be clusterized in conversation.

    * Must have at least 5 votes in conversation
    """
    num_votes = votes_in_conversation(user, conversation)
    if num_votes > 5:
        return True
    else:
        log.info(f'{user} only has {num_votes} and won\'t be clusterized')
        return False


#
# Stereotypes
#
@rules.register_perm('ej.can_manage_stereotypes')
def can_manage_stereotypes(user, conversation):
    """
    Check if user can manage stereotypes in conversation.

    * User can edit conversation
    """
    return user.has_perm('ej.can_edit_conversation', conversation)


#
# Auxiliary functions
#
def votes_in_conversation(user, conversation):
    """
    Return the number of votes of a user in conversation.
    """
    return conversation.user_votes(user).count()


def get_clusterization(obj):
    """
    Returns a clusterization from conversation or clusterization object.
    """
    if isinstance(obj, models.Clusterization):
        return obj
    elif isinstance(obj, Conversation):
        try:
            return obj.clusterization
        except obj.DoesNotExist:
            return None
    elif obj is None:
        raise TypeError('trying to call rule with a null clusterization object.\n'
                        'You probably forgot to pass the clusterization/conversation\n'
                        'to rules.test_rule() or user.has_perm()')
    else:
        msg = 'must be a clusterization or conversation object, got {}'
        raise TypeError(msg.format(obj.__class__.__name__))
