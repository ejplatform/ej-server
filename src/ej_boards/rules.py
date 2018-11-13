from constance import config
from django.conf import settings
from boogie import rules
from .models import Board


@rules.register_rule('ej_boards.has_board')
def has_board(user):
    """
    Verify if an user has a conversation board.
    """
    if Board.objects.filter(owner=user):
        return True
    else:
        return False


@rules.register_perm('ej_boards.can_add_board')
def can_add_board(user):
    """
    Verify if a user can create a board following the
    django admin permission and the max board number.
    """
    return (
        user.has_perm('ej_boards.add_board')
        or Board.objects.filter(owner=user).count() < config.EJ_MAX_BOARD_NUMBER
    )


@rules.register_perm('ej_boards.can_add_conversation')
def can_add_conversation(user, board):
    if board.owner == user:
        conversation_limit = rules.compute('ej_boards.conversation_limit', user)
        if board.conversations.count() < conversation_limit:
            return True
    return False


@rules.register_value('ej_boards.conversation_limit')
def conversation_limit(user):
    user_limit = user.limit_board_conversations
    if user_limit is not None:
        return user_limit
    else:
        return getattr(settings, 'EJ_BOARD_MAX_CONVERSATIONS', 50)
