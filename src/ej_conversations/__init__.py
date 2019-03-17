from .enums import Choice, RejectionReason

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
    if tags:
        conversation.tags.set(tags)
    return conversation
