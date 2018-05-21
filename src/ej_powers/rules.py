from rules import predicate


@predicate
def is_opinion_bridge(user, conversation):
    """
    Return true if user has the "opinion bridge"
    """


@predicate
def can_be_opinion_link(user, conversation):
    """
    Opinion bridges sits between two clusters and may help to promote dialogue
    between both clusters.
    """


@predicate
def is_group_activist(user, conversation):
    pass


@predicate
def can_be_group_activist(user, conversation):
    pass


#
# Powers
#
@predicate
def can_promote_comment(user, conversation):
    return conversation in self_promote_set(user)


@predicate
def can_promote_self_comment(user, conversation):
    return conversation in self_promote_set(user)


def promote_set(user):
    """
    Return all conversations that user can promote a comment.
    """


def self_promote_set(user):
    pass


