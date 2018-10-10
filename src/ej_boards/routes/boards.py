from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from . import urlpatterns
from ej_boards.forms import BoardForm


@urlpatterns.route('profile/boards/', template='ej_boards/list.jinja2', login=True)
def list(request):
    user = request.user
    boards = user.boards.all()
    can_add_board = user.has_perm('ej_boards.can_add_board')

    if not can_add_board and user.boards.count() == 1:
        return redirect(f'{boards[0].get_absolute_url()}conversations/')

    return {
        'boards': boards,
        'can_add_board': can_add_board,
    }


@urlpatterns.route('profile/boards/add/', login=True)
def create(request):
    user = request.user
    if not user.has_perm('ej_boards.can_add_board'):
        raise Http404

    form_class = BoardForm
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.owner = user
            board.save()

            return redirect(board.get_absolute_url())
    else:
        form = form_class()

    return {
        'content_title': _('Create board'),
        'form': form,
    }


#
# Conversation and boards management
#
@urlpatterns.route('<model:board>/edit/')
def edit(request, board):
    if request.user != board.owner:
        raise Http404
    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            form.instance.save()
            return redirect(board.get_absolute_url())
    else:
        form = BoardForm(instance=board)
    return {
        'form': form,
    }
