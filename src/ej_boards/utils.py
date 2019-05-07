from inspect import Signature

from django.http import Http404


def register_route(router, route, base_path, prefix):
    """
    Register copy of route in the given router object.
    """
    templates = route.template
    if isinstance(templates, (list, tuple)):
        templates = templates[0]
    if isinstance(templates, str):
        template_prefix, _, data = templates.partition("/")
        if template_prefix.startswith("ej_"):
            template_prefix = template_prefix[3:]
        templates = f"ej_boards/{template_prefix}-{data}"

    return router.register(
        make_view(route.function),
        path=base_path + route.path,
        name=prefix + "-" + route.name,
        login=route.login,
        perms=route.perms,
        template=templates,
    )


def make_view(view):
    if "request" in Signature.from_callable(view).parameters:
        return lambda request, board, **kwargs: view(
            request, check=check_board(board), **kwargs
        )
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

    def check_function(conversation, request):
        if not board.has_conversation(conversation):
            raise Http404
        if conversation.is_hidden and not request.user.has_perm(
            "ej.can_edit_conversation", conversation
        ):
            raise Http404
        conversation.board = board
        return conversation

    return check_function
