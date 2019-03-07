from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from boogie.router import Router
from ej_boards.models import Board
from ej_boards.utils import make_view, check_board
from ej_clusters.models import Stereotype
from ej_conversations import routes as conversations
from ej_conversations.models import Conversation
from ej_reports import routes as report
from .forms import BoardForm

app_name = 'ej_boards'
urlpatterns = Router(
    template=['ej_boards/{name}.jinja2', 'generic.jinja2'],
    models={
        'board': Board,
        'conversation': Conversation,
        'stereotype': Stereotype,
    },
    lookup_field={'board': 'slug'},
    lookup_type={'board': 'slug'},
)

# Constants
board_profile_admin_url = 'profile/boards/'
board_base_url = '<model:board>/conversations/'
board_conversation_url = board_base_url + '<model:conversation>/<slug:slug>/'
reports_url = '<model:board>/conversations/<model:conversation>/reports/'
reports_kwargs = {'login': True}


#
# Board URLs
#
@urlpatterns.route(board_profile_admin_url, login=True)
def board_list(request):
    user = request.user
    boards = user.boards.all()
    can_add_board = user.has_perm('ej.can_add_board')

    # Redirect to user's unique board, if that is the case
    if not can_add_board and user.boards.count() == 1:
        return redirect(f'{boards[0].get_absolute_url()}conversations/')

    return {'boards': boards, 'can_add_board': can_add_board}


@urlpatterns.route(board_profile_admin_url + 'add/', login=True, perms=['ej.can_add_board'])
def board_create(request):
    form = BoardForm(request=request)
    if form.is_valid_post():
        board = form.save(owner=request.user)
        return redirect(board.get_absolute_url())
    return {'form': form}


@urlpatterns.route('<model:board>/edit/', perms=['ej.can_edit_board:board'])
def board_edit(request, board):
    form = BoardForm(instance=board, request=request)
    form.fields['slug'].help_text = _('You cannot change this value')
    form.fields['slug'].disabled = True

    if form.is_valid_post():
        form.save()
        return redirect(board.get_absolute_url())
    return {'form': form, 'board': board}


#
# Conversation URLs
#
@urlpatterns.route(board_base_url)
def conversation_list(request, board):
    return conversations.conversation_list(
        request,
        queryset=board.conversations.annotate_attr(board=board),
        add_perm='ej.can_edit_board',
        perm_obj=board,
        context={'board': board},
        url=reverse('boards:conversation-create', kwargs={'board': board}),
    )


@urlpatterns.route(board_base_url + 'add/', perms=['ej.can_edit_board:board'])
def conversation_create(request, board):
    return conversations.create(request, board=board, context={'board': board})


@urlpatterns.route(board_conversation_url)
def conversation_detail(request, board, **kwargs):
    return conversations.detail(request, **kwargs, check=check_board(board))


@urlpatterns.route(board_conversation_url + 'edit/', perms=['ej.can_edit_conversation:conversation'])
def conversation_edit(request, board, **kwargs):
    return conversations.edit(request, board=board, check=check_board(board), **kwargs)


@urlpatterns.route(board_conversation_url + 'moderate/', perms=['ej.can_edit_conversation:conversation'])
def conversation_moderate(request, board, **kwargs):
    return conversations.moderate(request, check=check_board(board), **kwargs)


#
# Reports
#
for view in report.loose_perms_views + report.strict_perms_views:
    urlpatterns.register(
        make_view(view),
        path=f'{board_base_url}{report.urlpatterns.base_path}{view.route.path}',
        name='report-' + view.route.name,
        login=True,
        perms=view.route.perms,
        template=view.route.template[0].replace('ej_reports/', 'ej_boards/report-'),
    )
