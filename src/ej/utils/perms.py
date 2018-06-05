from ej_conversations.models import Conversation


def conversations(user, rules):
    """
    Return a list with all conversations and
    their respective rules applied relative to
    the given user.
    """
    conversations = []
    perms = {}
    for conversation in Conversation.objects.all():
        for rule in rules:
            perms[rule.__name__] = rule(user, conversation)
        conversations.append((conversation, perms))

    return conversations
