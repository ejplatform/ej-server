default_app_config = 'ej_gamification.apps.EjGamificationConfig'

from .functions import promote_comment, is_promoted


def get_participation(user, conversation, sync=False):
    """
    Return a valid ParticipationProgress() for user.
    """
    progress, created = user.participation_progresses.get_or_create(conversation=conversation)
    if created:
        progress.sync().save()
        return progress
    if sync:
        progress.sync().save()
    return progress


def get_progress(obj, sync=False):
    """
    Return a valid ConversationProgress() or UserProgress() for object.
    """
    from .models import UserProgress, ConversationProgress
    from ej_conversations.models import Conversation

    try:
        progress = obj.progress
    except AttributeError:
        if isinstance(obj, Conversation):
            progress = ConversationProgress(conversation=obj).sync()
        else:
            progress = UserProgress(user=obj).sync()
        progress.save()
        print(obj, progress)
        return progress

    if sync:
        progress.sync().save()
    return progress
