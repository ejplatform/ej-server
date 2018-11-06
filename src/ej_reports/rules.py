from boogie import rules


@rules.register_perm('ej.can_view_report')
def can_edit_conversation(user, conversation):
    """
    Can edit a given conversation.

    * User can edit conversation
    * OR user has explict permission to see reports (not implemented)
    """
    if user.has_perm('ej.can_edit_conversation', conversation):
        return True
    else:
        return False
