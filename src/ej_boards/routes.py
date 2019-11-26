from boogie.router import Router
from django.apps import apps
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from ej_boards.models import Board
from ej_boards.utils import check_board, register_route
from ej_clusters.models import Stereotype
from ej_conversations import routes as conversations
from ej_conversations.models import Conversation
from .forms import BoardForm

app_name = "ej_boards"
urlpatterns = Router(
    template=["ej_boards/{name}.jinja2", "generic.jinja2"],
    models={"board": Board, "conversation": Conversation, "stereotype": Stereotype},
    lookup_field={"board": "slug"},
    lookup_type={"board": "slug"},
)

# Constants
BOARD_PROFILE_ADMIN_URL = "profile/boards/"
BOARD_BASE_URL = "<model:board>/conversations/"
BOARD_CONVERSATION_URL = BOARD_BASE_URL + "<model:conversation>/<slug:slug>/"
REPORTS_URL = "<model:board>/conversations/<model:conversation>/reports/"
REPORTS_KWARGS = {"login": True}


#
# Board URLs
#
@urlpatterns.route(BOARD_PROFILE_ADMIN_URL, login=True)
def board_list(request):
    user = request.user
    boards = user.boards.all()
    can_add_board = user.has_perm("ej.can_add_board")

    # Redirect to user's unique board, if that is the case
    if not can_add_board and user.boards.count() == 1:
        return redirect(f"{boards[0].get_absolute_url()}conversations/")

    return {"boards": boards, "can_add_board": can_add_board}


@urlpatterns.route(BOARD_PROFILE_ADMIN_URL + "add/", login=True, perms=["ej.can_add_board"])
def board_create(request):
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
    return {"form": form, "board": board}


#
# Conversation URLs
#
@urlpatterns.route(BOARD_BASE_URL)
def conversation_list(request, board):
    return conversations.list_view(
        request, queryset=board.conversations.annotate_attr(board=board), context={"board": board}
    )


@urlpatterns.route(BOARD_BASE_URL + "add/", perms=["ej.can_edit_board:board"])
def conversation_create(request, board):
    return conversations.create(request, board=board, context={"board": board})


@urlpatterns.route(BOARD_CONVERSATION_URL, login=True)
def conversation_detail(request, board, **kwargs):
    return conversations.detail(request, **kwargs, check=check_board(board))


@urlpatterns.route(BOARD_CONVERSATION_URL + "edit/", perms=["ej.can_edit_conversation:conversation"])
def conversation_edit(request, board, **kwargs):
    return conversations.edit(request, board=board, check=check_board(board), **kwargs)


@urlpatterns.route(BOARD_CONVERSATION_URL + "moderate/", perms=["ej.can_edit_conversation:conversation"])
def conversation_moderate(request, board, **kwargs):
    return conversations.moderate(request, check=check_board(board), **kwargs)


#
# Dataviz
#
if apps.is_installed("ej_dataviz"):
    from ej_dataviz import routes as dataviz
    from ej_dataviz import routes_report as report

    base_path = BOARD_BASE_URL + dataviz.urlpatterns.base_path
    for route in dataviz.urlpatterns.routes:
        register_route(urlpatterns, route, base_path, "dataviz")

    base_path = BOARD_BASE_URL + report.urlpatterns.base_path
    for route in report.urlpatterns.routes:
        register_route(urlpatterns, route, base_path, "report")

#
# Clusters
#
if apps.is_installed("ej_clusters"):
    from ej_clusters import routes as cluster

    base_path = BOARD_BASE_URL + cluster.urlpatterns.base_path
    for route in cluster.urlpatterns.routes:
        register_route(urlpatterns, route, base_path, "cluster")
