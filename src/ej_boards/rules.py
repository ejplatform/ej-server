from boogie import rules
from .models import Board
from constance import config


@rules.register_rule('ej_boards.has_board')
def has_board(user):
    """
    Verify if an user has a conversation board.
    """
    if Board.objects.filter(owner=user):
        return True
    else:
        return False


@rules.register_rule('ej_boards.can_create_board')
def can_create_board(user):
    """
    Verify if a user can create a board following the
    max board number.
    """
    return Board.objects.filter(owner=user).count() < config.MAX_BOARD_NUMBER


@rules.register_perm('ej_boards.can_add_conversation')
def can_add_conversation(user, board):
    if board.owner == user:
        return True

    return False
