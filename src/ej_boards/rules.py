from constance import config

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
    return board.owner == user


@rules.register_value('ej.maximum_number_of_boards')
def number_of_boards(user):
    """
    Return the number of boards user can create.
    """
    if user.is_superuser:
        return float('inf')
    return config.EJ_MAX_BOARD_NUMBER
