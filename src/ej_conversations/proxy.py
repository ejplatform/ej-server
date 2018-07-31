from boogie.rules import proxy_seq
from ej_conversations.models import Conversation


def conversations_with_moderation(user, qs=None):
    perm = 'ej_conversations.can_moderate_conversation'
    kwargs = {
        'can_moderate': lambda x: user.has_perm(perm, x)
    }
    if qs is None:
        qs = Conversation.objects.filter(is_promoted=True)
    return proxy_seq(qs, user=user, **kwargs)
