import logging

from django.db.models import Count

from boogie import rules
from . import models

log = logging.getLogger('ej')


@rules.register_rule('ej_clusters.conversation_has_sufficient_data')
def conversation_has_sufficient_data(conversation):
    """
    Check if conversation has sufficient data to start clusterization.

    * Has at least 5 comments with at least 5 votes.
    * Has at least 2 clusters with at least 1 registered stereotype.
    """
    filled_comments = (
        conversation.comments
            .annotate(count=Count('votes'))
            .filter(count__gte=5)
            .count()
    )
    filled_clusters = (
        models.get_clusterization(conversation).clusters
            .annotate(count=Count('stereotypes'))
            .filter(count__gte=1)
            .count()
    )
    return filled_comments >= 5 and filled_clusters >= 2


@rules.register_rule('ej_clusters.must_update_clusters')
def must_update_clusters(conversation):
    """
    Check if it requires a full re-clusterization.

    * Has at least 5 unprocessed votes
    * (or) Has at least 1 unprocessed comments with 5 or more votes
    """
    manager = models.get_clusterization(conversation)
    return (
        manager.unprocessed_votes >= 5
        or manager.unprocessed_comments >= 1
    )


@rules.register_perm('ej_clusters.can_be_clusterized')
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
# Auxiliary functions
#
def votes_in_conversation(user, conversation):
    """
    Return the number of votes of a user in conversation.
    """
    return conversation.user_votes(user).count()
