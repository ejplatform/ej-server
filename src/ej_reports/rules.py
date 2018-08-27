from boogie import rules


@rules.register_perm('ej_reports.can_view_report')
def can_edit_conversation(user, conversation):
    """
    Can edit a given conversation.

    * User can edit conversation
    * OR user has explict permission to see reports (not implemented)
    """
    print(user, conversation)

    if user.has_perm('ej.can_edit_conversation', conversation):
        return True
    else:
        # Not implemented yet!
        return False
