from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from boogie.router import Router
from ej_boards.models import Board
from ej_boards.utils import make_view, assure_correct_board, check_board
from ej_clusters import routes as clusters
from ej_clusters.models import Stereotype
from ej_conversations import routes as conversations
from ej_conversations.models import Conversation
from ej_reports import routes as report
from .forms import BoardForm

app_name = 'ej_boards'

#
# Board management
#
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
board_conversations_url = board_base_url + '<model:conversation>/<slug:slug>/'
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
    return {'form': form}


#
# Conversation URLs
#
@urlpatterns.route(board_base_url)
def conversation_list(request, board):
    # Attach board to each conversation
    conversations_ = []
    for conversation in board.conversations.all():
        conversation.board = board
        conversations_.append(conversation)

    # Call super method
    return conversations.conversation_list(
        request,
        queryset=conversations_,
        new_perm='ej.can_edit_board',
        perm_obj=board,
        url=reverse('boards:conversation-create', kwargs={'board': board}),
    )


@urlpatterns.route(board_base_url + 'add/', perms=['ej.can_edit_board:board'])
def conversation_create(request, board):
    return conversations.create(request, board=board)


@urlpatterns.route(board_conversations_url)
def conversation_detail(request, board, **kwargs):
    return conversations.detail(request, **kwargs, check=check_board(board))


@urlpatterns.route(board_conversations_url + 'edit/', perms=['ej.can_edit_conversation:conversation'])
def conversation_edit(request, board, **kwargs):
    return conversations.edit(request, board=board, check=check_board(board), **kwargs)


@urlpatterns.route(board_conversations_url + 'moderate/', perms=['ej.can_edit_conversation:conversation'])
def conversation_moderate(request, board, **kwargs):
    return conversations.moderate(request, check=check_board(board), **kwargs)


#
# Stereotypes and clusters
#
@urlpatterns.route('<model:board>/conversations/<model:conversation>/stereotypes/',
                   perms=['ej.can_manage_stereotypes:conversation'])
def stereotype_list(board, conversation):
    assure_correct_board(conversation, board)
    return clusters.stereotype_list_context(conversation)


@urlpatterns.route('<model:board>/conversations/<model:conversation>/stereotypes/add/',
                   perms=['ej.can_manage_stereotypes:conversation'])
def stereotype_create(request, board, conversation):
    assure_correct_board(conversation, board)
    return clusters.create_stereotype_context(request, conversation)


@urlpatterns.route('<model:board>/conversations/<model:conversation>/stereotypes/<model:stereotype>/edit/',
                   perms=['ej.can_manage_stereotypes:conversation'])
def stereotype_edit(request, board, conversation, stereotype):
    assure_correct_board(conversation, board)
    return clusters.edit_stereotype_context(request, conversation, stereotype)


#
# Reports
#
for view in report.loose_perms_views:
    urlpatterns.register(
        make_view(view),
        path=board_base_url + view.route.path,
        name='report-' + view.route.name,
        template=view.route.template[0].replace('ej_reports/', 'ej_boards/report-')
    )

for view in report.strict_perms_views:
    urlpatterns.register(
        make_view(view),
        path=board_base_url + view.route.path,
        name='report-' + view.route.name,
        template=view.route.template[0].replace('ej_reports/', 'ej_boards/report-'),
        perms=report.strict_perms,
    )
