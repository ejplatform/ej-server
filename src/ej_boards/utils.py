from inspect import Signature

from django.http import Http404


def make_view(view):
    if 'request' in Signature.from_callable(view).parameters:
        return lambda request, board, **kwargs: view(request, check=check_board(board), **kwargs)
    else:
        return lambda board, **kwargs: view(check=check_board(board), **kwargs)


def assure_correct_board(conversation, board):
    """
    Raise 404 if conversation does not belong to board.
    """
    if not board.has_conversation(conversation):
        raise Http404
    conversation.board = board


def check_board(board):
    """
    Raise 404 if conversation does not belong to board.
    """

    def check_function(conversation):
        if not board.has_conversation(conversation):
            raise Http404
        conversation.board = board
        return conversation

    return check_function
