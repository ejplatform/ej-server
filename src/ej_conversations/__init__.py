from sidekick import import_later

__version__ = '0.1.0b'
_db = import_later('.models', package=__package__)
default_app_config = 'ej_conversations.apps.EjConversationsConfig'


def create_conversation(text, title, author, *, is_promoted=False, tags=(), commit=True):
    """
    Creates a new conversation object and saves it in the database.
    """
    conversation = _db.Conversation(text=text, title=title, author=author, is_promoted=is_promoted)
    conversation.clean()
    if commit:
        conversation.save()
    return conversation
