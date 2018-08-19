from sidekick import import_later

__version__ = '0.1.0b'
default_app_config = 'ej_conversations.apps.EjConversationsConfig'


def create_conversation(text, title, author, *, is_promoted=False, tags=(), commit=True):
    """
    Creates a new conversation object and saves it in the database.
    """
    from .models import Conversation

    conversation = Conversation(text=text, title=title, author=author, is_promoted=is_promoted)
    conversation.clean()
    if commit:
        conversation.save()
    return conversation
