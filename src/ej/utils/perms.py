from ej_conversations.models import Conversation


def conversations(user, rules, queryset=Conversation.objects.all()):
    """
    Return a list with all conversations and
    their respective rules applied relative to
    the given user.
    """
    conversations = []
    for conversation in queryset:
        perms = {}
        for rule in rules:
            perms[rule.__name__] = rule(user, conversation)
        conversations.append((conversation, perms))

    return conversations
