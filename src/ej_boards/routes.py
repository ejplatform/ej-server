from boogie.router import Router
from django.apps import apps
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render

from ej_boards.models import Board
from ej_users.models import User
from ej_boards.utils import patched_register_app_routes, register_app_routes
from ej_clusters.models import Stereotype
from ej_conversations.models import Conversation
from ej_signatures.models import SignatureFactory
from ej_tools.urls import urlpatterns as conversation_tools_urlpatterns
from ej_conversations.urls import urlpatterns as conversation_urlpatterns
from .forms import BoardForm
from ej_tools.models import RasaConversation, ConversationMautic
from ej_dataviz import routes as dataviz
from ej_dataviz import routes_report as report
from ej_clusters import routes as cluster
from django.core.paginator import Paginator
from .utils import (
    PAGINATOR_START_PAGE,
    PAGE_ELEMENTS_COUNT,
    NUM_ENTRIES_DEFAULT,
)

from ej_conversations.urls import conversation_url
from .utils import apply_user_filters, apply_conversation_filters, apply_board_filters

app_name = "ej_boards"
urlpatterns = Router(
    template=["ej_boards/{name}.jinja2", "generic.jinja2"],
    models={
        "board": Board,
        "conversation": Conversation,
        "stereotype": Stereotype,
        "connection": RasaConversation,
        "mautic_connection": ConversationMautic,
    },
    lookup_field={"board": "slug"},
    lookup_type={"board": "slug"},
)

# Constants
board_profile_admin_url = "profile/boards/"
board_base_url = "<model:board>/conversations/"
board_conversation_url = board_base_url + conversation_url
reports_url = "<model:board>/conversations/<model:conversation>/reports/"
reports_kwargs = {"login": True}

#
# Board URLs
#


@urlpatterns.route(board_profile_admin_url, login=True)
def board_list(request):
    user = request.user
    boards = user.boards.all()
    can_add_board = user.has_perm("ej.can_add_board")

    # Redirect to user's unique board, if that is the case
    if not can_add_board and user.boards.count() == 1:
        return redirect(f"{boards[0].get_absolute_url()}")

    return {"boards": boards, "can_add_board": can_add_board}


@urlpatterns.route(
    board_profile_admin_url + "environment/", login=True, perms=["ej.can_access_environment_management"]
)
def environment(request):
    boards_count = Board.objects.count()
    conversations_count = Conversation.objects.count()
    users_count = User.objects.count()

    return {
        "user_boards": Board.objects.filter(owner=request.user),
        "boards_count": boards_count,
        "conversations_count": conversations_count,
        "users_count": users_count,
    }


@urlpatterns.route(
    board_profile_admin_url + "environment/recent-boards/",
    login=True,
    perms=["ej.can_access_environment_management"],
)
def get_recent_boards(request):
    page = int(request.GET.get("page", PAGINATOR_START_PAGE))
    board_is_active = True if request.GET.get("boardIsActive", "true") == "true" else False

    if board_is_active:
        recent_boards = Board.objects.filter(conversation__gte=1).distinct().order_by("-created")
    else:
        recent_boards = Board.objects.order_by("-created")

    paginator = Paginator(recent_boards, PAGE_ELEMENTS_COUNT)
    recent_boards = paginator.get_page(page)
    recent_boards.adjusted_elided_pages = paginator.get_elided_page_range(
        recent_boards.number, on_each_side=1, on_ends=1
    )

    return render(
        request,
        "ej_boards/environment/recent-boards.jinja2",
        {
            "recent_boards": recent_boards,
        },
    )


@urlpatterns.route(
    board_profile_admin_url + "environment/searched-users/",
    login=True,
    perms=["ej.can_access_environment_management"],
)
def get_searched_users(request):
    num_entries = request.GET.get("numEntries", NUM_ENTRIES_DEFAULT)
    order_by = request.GET.get("orderBy", "date")
    sort = request.GET.get("sort", "desc")
    search_string = request.GET.get("searchString", "")
    page = int(request.GET.get("page", PAGINATOR_START_PAGE))

    searched_users = apply_user_filters(order_by, sort, search_string)

    paginator = Paginator(searched_users, num_entries)

    page_object = paginator.get_page(page)
    page_object.adjusted_elided_pages = paginator.get_elided_page_range(
        page_object.number, on_each_side=1, on_ends=1
    )

    return render(
        request,
        "ej_boards/environment/searched-users.jinja2",
        {
            "page_object": page_object,
        },
    )


@urlpatterns.route(
    board_profile_admin_url + "environment/searched-boards/",
    login=True,
    perms=["ej.can_access_environment_management"],
)
def get_searched_boards(request):
    num_entries = request.GET.get("numEntries", NUM_ENTRIES_DEFAULT)
    order_by = request.GET.get("orderBy")
    sort = request.GET.get("sort", "desc")
    search_string = request.GET.get("searchString", "")
    page = int(request.GET.get("page", PAGINATOR_START_PAGE))

    searched_boards = apply_board_filters(order_by, sort, search_string)

    paginator = Paginator(searched_boards, num_entries)

    page_object = paginator.get_page(page)
    page_object.adjusted_elided_pages = paginator.get_elided_page_range(
        page_object.number, on_each_side=1, on_ends=1
    )

    return render(
        request,
        "ej_boards/environment/searched-boards.jinja2",
        {
            "page_object": page_object,
        },
    )


@urlpatterns.route(
    board_profile_admin_url + "environment/searched-conversations/",
    login=True,
    perms=["ej.can_access_environment_management"],
)
def get_searched_conversations(request):
    num_entries = request.GET.get("numEntries", NUM_ENTRIES_DEFAULT)
    order_by = request.GET.get("orderBy")
    sort = request.GET.get("sort", "desc")
    search_string = request.GET.get("searchString", "")
    page = int(request.GET.get("page", PAGINATOR_START_PAGE))

    searched_conversations = apply_conversation_filters(order_by, sort, search_string)

    paginator = Paginator(searched_conversations, num_entries)

    page_object = paginator.get_page(page)
    page_object.adjusted_elided_pages = paginator.get_elided_page_range(
        page_object.number, on_each_side=1, on_ends=1
    )

    return render(
        request,
        "ej_boards/environment/searched-conversations.jinja2",
        {
            "page_object": page_object,
        },
    )


@urlpatterns.route(board_profile_admin_url + "add/", login=True)
def board_create(request):  # TODO arrumar o navigation dele
    form = BoardForm(request=request)
    if form.is_valid_post():
        board = form.save(owner=request.user)
        return redirect(board.get_absolute_url())
    return {"form": form}


@urlpatterns.route("<model:board>/edit/", perms=["ej.can_edit_board:board"])
def board_edit(request, board):
    form = BoardForm(instance=board, request=request)
    form.fields["slug"].help_text = _("You cannot change this value")
    form.fields["slug"].disabled = True

    if form.is_valid_post():
        form.save()
        return redirect(board.get_absolute_url())
    return {"form": form, "board": board, "user_boards": Board.objects.filter(owner=request.user)}


#
# Conversation URLs
#
@urlpatterns.route("<model:board>/")
def board_base(request, board):
    return redirect(board.get_absolute_url())


@urlpatterns.route(board_base_url + "tour/", login=True)  # TODO: passar essa rota para o ej_conversations
def tour(request, board):
    user = request.user
    if user.get_profile().completed_tour:
        return redirect(f"{board.get_absolute_url()}")
    if request.method == "POST":
        user.get_profile().completed_tour = True
        user.get_profile().save()
        return redirect(f"{board.get_absolute_url()}")
    user_signature = SignatureFactory.get_user_signature(user)
    max_conversation_per_user = user_signature.get_conversation_limit()
    return {
        "conversations": board.conversations.annotate_attr(board=board),
        "help_title": _(
            "Welcome to EJ. This is your personal board. Board is where your conversations will be available. Press 'New conversation' to starts collecting yours audience opinion."
        ),
        "conversations_limit": max_conversation_per_user,
        "board": board,
    }


register_app_routes(dataviz, board_base_url, urlpatterns, "dataviz")
register_app_routes(report, board_base_url, urlpatterns, "report")
register_app_routes(cluster, board_base_url, urlpatterns, "cluster")
patched_register_app_routes(urlpatterns.urls, conversation_tools_urlpatterns, "conversation-tools")
patched_register_app_routes(urlpatterns.urls, conversation_urlpatterns, "conversation")
