from inspect import Signature
from django.urls import path

from django.http import Http404
from django.core.paginator import EmptyPage, PageNotAnInteger


PAGINATOR_START_PAGE = 1
PAGE_ELEMENTS_COUNT = 12

MAX_PAGINATOR_ITEMS = 7
ELLIPSE_LIMIT = 5


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
        return lambda request, board, **kwargs: view(request, board=board, **kwargs)
    else:
        return lambda **kwargs: view(**kwargs)


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
        if conversation.is_hidden and not request.user.has_perm("ej.can_edit_conversation", conversation):
            raise Http404
        conversation.board = board
        return conversation

    return check_function


def register_app_routes(app_routes, board_base_url, urlpatterns, route_name):
    base_path = board_base_url + app_routes.urlpatterns.base_path
    for route in app_routes.urlpatterns.routes:
        register_route(urlpatterns, route, base_path, route_name)


def patched_register_app_routes(board_urls, app_urls, app_name):
    """
    Register an app's routes in the boards namespace using django's default routes, not boogie's.
    """
    for url in app_urls:
        board_url = "<slug:board_slug>/conversations/" + str(url.pattern)
        view = url.callback
        pattern = path(board_url, view, name=f"{app_name}-{url.name}")
        board_urls.append(pattern)
    return board_urls


def statistics(board):
    """
    Return a dictionary with basic statistics about board.
    """
    votes = 0
    participants = 0
    conversations = 0

    for conversation in board.conversations:
        stats = conversation.statistics()
        votes += stats["votes"]["total"]
        participants += stats["participants"]["voters"]
        conversations += 1

    return {"votes": votes, "participants": participants, "conversations": conversations}


def get_page(paginator, page):
    """
    Gets the boards from a specific page.
    """
    if page < 1:
        page = 1
    if page > paginator.num_pages:
        page = paginator.num_pages

    try:
        recent_boards = paginator.page(page)
    except PageNotAnInteger:
        recent_boards = paginator.page(1)
    except EmptyPage:
        recent_boards = paginator.page(paginator.num_pages)

    return recent_boards


def get_paginator_visible_pages(current_page, num_pages, page_range):
    if num_pages <= MAX_PAGINATOR_ITEMS:
        mode = "no_ellipse"
        pages = page_range
    elif current_page <= ELLIPSE_LIMIT:
        mode = "ellipse_end"
        pages = page_range[:ELLIPSE_LIMIT]
    elif current_page > num_pages - ELLIPSE_LIMIT:
        mode = "ellipse_start"
        pages = page_range[-ELLIPSE_LIMIT:]
    else:
        mode = "ellipse_both"
        pages = [(current_page - 1), current_page, (current_page + 1)]

    return {"mode": mode, "pages": pages}
