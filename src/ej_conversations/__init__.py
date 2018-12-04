from django.utils.translation import ugettext_lazy as _
from sidekick import import_later

from boogie.fields import IntEnum

__version__ = '0.1.0b'
default_app_config = 'ej_conversations.apps.EjConversationsConfig'


def create_conversation(text, title, author, *, is_promoted=False, tags=(), commit=True, **kwargs):
    """
    Creates a new conversation object and saves it in the database.
    """
    from .models import Conversation

    conversation = Conversation(text=text, title=title, author=author, is_promoted=is_promoted, **kwargs)
    conversation.clean()
    if commit:
        conversation.save()
    return conversation


class Choice(IntEnum):
    SKIP = 0, _('Skip')
    AGREE = 1, _('Agree')
    DISAGREE = -1, _('Disagree')
