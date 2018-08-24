from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from autoslug.settings import slugify
from . import urlpatterns, conversation_url
from .. import forms, models
from ej_boards.models import Board, BoardSubscription
from ej_boards.forms import BoardForm


@urlpatterns.route('add/', login=True, perms=['ej_conversations.can_add_conversation'])
def create(request):
    form_class = forms.ConversationForm
    boards = []
    if request.method == 'POST':
        form = form_class(request.POST)

        if form.is_valid():
            conversation = form.save(commit=False)
            conversation.author = request.user
            board = get_board_in_form(form, request)
            conversation.save()
            if board:
                BoardSubscription.objects.create(conversation=conversation, board=board)

            for tag in form.cleaned_data['tags']:
                conversation.tags.add(tag)

            n = int(form.data['commentscount']) + 1
            for i in range(1, n):
                name = 'comment-' + str(i)
                if name in form.data and form.data[name]:
                    models.Comment.objects.create(
                        content=form.data[name],
                        conversation=conversation,
                        author=request.user,
                        status=models.Comment.STATUS.approved,
                    )

            return redirect(conversation.get_absolute_url() + 'stereotypes/')
    else:
        form = form_class()
        boards = request.user.boards.all()

    return {
        'form': form,
        'boards': boards,
    }


@urlpatterns.route(conversation_url + 'edit/',
                   perms=['ej_conversations.can_edit_conversation'])
def edit(request, conversation):
    comments = []
    board = None
    if request.method == 'POST':
        form = forms.ConversationForm(
            data=request.POST,
            instance=conversation,
        )
        if form.is_valid():
            form.instance.save()
            return redirect(conversation.get_absolute_url() + 'moderate/')
    else:
        boards = BoardSubscription.objects.filter(conversation=conversation)
        if boards.count() > 0:
            board = boards[0].board
        form = forms.ConversationForm(instance=conversation)
        for comment in models.Comment.objects.filter(conversation=conversation, status='pending'):
            if comment.is_pending:
                comments.append(comment)

    return {
        'conversation': conversation,
        'comments': comments,
        'board': board,
        'form': form,
    }


@urlpatterns.route(conversation_url + 'moderate/')
def moderate(request, conversation):
    if not request.user.has_perm('ej_conversations.can_moderate_conversation', conversation):
        raise Http404

    comments = []
    if request.method == 'POST':
        comment = models.Comment.objects.get(id=request.POST['comment'])
        comment.status = comment.STATUS.approved if request.POST['vote'] == 'approve' else comment.STATUS.rejected
        comment.rejection_reason = request.POST['rejection_reason']
        comment.save()

    for comment in models.Comment.objects.filter(conversation=conversation, status='pending'):
        if comment.is_pending:
            comments.append(comment)
    return {
        'conversation': conversation,
        'comments': comments,
    }


def get_board_in_form(form, request):
    if 'board' in form.data:
        board = Board.objects.get(pk=int(form.data['board']))
    elif 'newboard' in form.data:
        board_form = create_board_form(form)
        if board_form.is_valid():
            board = board_form.save(commit=False)
            board.owner = request.user
            board.save()
        else:
            form.add_error('title', _('Board with this slug already exists!'))
            return {
                'form': form,
                'boards': request.user.boards.all(),
            }
    else:
        board = None
    return board


def create_board_form(form):
    title = form.data['newboard']
    data = {'title': title, 'description': '', 'slug': slugify(title)}
    board_form = BoardForm(data)
    return board_form
