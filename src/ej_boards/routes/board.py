from django.shortcuts import redirect, Http404
from django.utils.translation import ugettext_lazy as _
from boogie.router import Router
from ..models import Board
from ..forms import BoardForm


app_name = 'ej_boards'
urlpatterns = Router(
    template=['ej_boards/{name}.jinja2', 'generic.jinja2'],
    models={
        'board': Board,
    },
    lookup_field='slug',
    lookup_type='slug',
)
board_url = '<model:board>'


@urlpatterns.route('add/')
def create(request):
    form_class = BoardForm
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.owner = request.user
            board.save()

            return redirect(board.get_absolute_url())
    else:
        form = form_class()

    return {
        'content_title': _('Create board'),
        'form': form,
    }


@urlpatterns.route('', template='ej_boards/list.jinja2')
def board_list(request):
    user = request.user
    return {
        'boards': user.boards.all()
    }


# @urlpatterns.route(board_url)
# def detail(request, board, conversation):
#     return {
#         'board': board,
#         'conversation': conversation,
#     }


@urlpatterns.route(board_url + '/edit/', template='ej_boards/create.jinja2')
def edit(request, board):
    user = request.user
    if user != board.owner:
        raise Http404
    form_class = BoardForm
    if request.method == 'POST':
        form = form_class(
            instance=board,
            data=request.POST
        )
        if form.is_valid():
            form.instance.save()
            return redirect(board.get_absolute_url())
    else:
        form = form_class(instance=board)
    return {
        'form': form,
    }
