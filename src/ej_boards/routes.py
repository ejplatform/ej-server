from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from boogie.router import Router
from ej_boards.models import Board
from ej_clusters import routes as cluster_routes
from ej_clusters.models import Stereotype
from ej_conversations import forms
from ej_conversations.forms import CommentForm
from ej_conversations.models import Conversation, Vote
from ej_reports import routes as report_routes
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
    lookup_field={'conversation': 'slug', 'board': 'slug'},
    lookup_type={'conversation': 'slug', 'board': 'slug'},
)


#
# Conversation URLs
#
@urlpatterns.route('<model:board>/conversations/')
def conversation_list(request, board):
    user = request.user
    conversations = board.conversations.filter(is_hidden=False)
    board_user = board.owner
    boards = []
    boards_count = 0
    if user == board_user:
        boards = board_user.boards.all()
        boards_count = boards.count()
        user_is_owner = True
    else:
        user_is_owner = False
    return {
        'can_add_conversation': user.has_perm('ej.can_add_conversation_to_board', board),
        'can_edit_board': user_is_owner,
        'create_url': reverse('boards:conversation-create', kwargs={'board': board}),
        'edit_url': reverse('boards:board-edit', kwargs={'board': board}),
        'conversations': conversations,
        'boards_count': boards_count,
        'boards': boards,
        'current_board': board,
        'title': board.title,
        'description': board.description,
        'show_welcome_window': False,
        'board_palette': board.css_palette
    }


@urlpatterns.route('<model:board>/conversations/add/')
def conversation_create(request, board):
    user = request.user
    if not user == board.owner:
        raise Http404

    form = forms.ConversationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            conversation = form.save_comments(author=user,board=board)
        kwargs = {'board': board, 'conversation': conversation}
        return redirect(reverse('boards:conversation-stereotype-list', kwargs=kwargs))

    return {'form': form}


@urlpatterns.route('<model:board>/conversations/<model:conversation>/')
def conversation_detail(request, board, conversation):
    assure_correct_board(conversation, board)
    return get_conversation_detail_context(request, conversation)


@urlpatterns.route('<model:board>/conversations/<model:conversation>/edit/',
                   perms=['ej.can_edit_conversation:conversation'])
def conversation_edit(request, board, conversation):
    assure_correct_board(conversation, board)
    ctx = get_conversation_edit_context(request, conversation, board)
    ctx['board'] = board
    return ctx


@urlpatterns.route('<model:board>/conversations/<model:conversation>/moderate/',
                   perms=['ej.can_edit_conversation:conversation'])
def conversation_moderate(request, board, conversation):
    assure_correct_board(conversation, board)
    return get_conversation_moderate_context(request, conversation)


@urlpatterns.route('<model:board>/conversations/<model:conversation>/stereotypes/',
                   perms=['ej.can_manage_stereotypes:conversation'])
def conversation_stereotype_list(board, conversation):
    assure_correct_board(conversation, board)
    return cluster_routes.stereotype_list_context(conversation)


@urlpatterns.route('<model:board>/conversations/<model:conversation>/stereotypes/add/',
                   perms=['ej.can_manage_stereotypes:conversation'])
def conversation_stereotype_create(request, board, conversation):
    assure_correct_board(conversation, board)
    return cluster_routes.create_stereotype_context(request, conversation)


@urlpatterns.route('<model:board>/conversations/<model:conversation>/stereotypes/<model:stereotype>/edit/',
                   perms=['ej.can_manage_stereotypes:conversation'])
def conversation_stereotype_edit(request, board, conversation, stereotype):
    assure_correct_board(conversation, board)
    return cluster_routes.edit_stereotype_context(request, conversation, stereotype)


#
# Board URLs
#
@urlpatterns.route('profile/boards/', login=True)
def board_list(request):
    user = request.user
    boards = user.boards.all()
    can_add_board = user.has_perm('ej.can_add_board')

    if not can_add_board and user.boards.count() == 1:
        return redirect(f'{boards[0].get_absolute_url()}conversations/')

    return {
        'boards': boards,
        'can_add_board': can_add_board,
    }


@urlpatterns.route('profile/boards/add/', login=True)
def board_create(request):
    user = request.user
    if not user.has_perm('ej.can_add_board'):
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


# Conversation and boards management
@urlpatterns.route('<model:board>/edit/', perms=['ej.can_edit_board:board'])
def board_edit(request, board):
    if request.method == 'POST':
        form = BoardForm(request.POST, request.FILES, instance=board)
        if form.is_valid():
            form.instance.save()
            return redirect(board.get_absolute_url())
    else:
        form = BoardForm(instance=board)
    return {
        'form': form,
    }


#
# Reports
#
reports_url = '<model:board>/conversations/<model:conversation>/reports/'
reports_kwargs = {'login': True}


@urlpatterns.route(reports_url, **reports_kwargs)
def report(request, board, conversation):
    assure_correct_board(conversation, board)
    return report_routes.index(request, conversation)


@urlpatterns.route(reports_url + 'participants/', staff=True, **reports_kwargs)
def report_participants(board, conversation):
    assure_correct_board(conversation, board)
    return report_routes.participants_table(conversation)


@urlpatterns.route(reports_url + 'scatter/', **reports_kwargs)
def report_scatter(board, conversation):
    assure_correct_board(conversation, board)
    return report_routes.scatter(conversation)


@urlpatterns.route(reports_url + 'votes.<format>', **reports_kwargs)
def report_votes_data(board, conversation, format):
    assure_correct_board(conversation, board)
    return report_routes.votes_data(conversation, format)


@urlpatterns.route(reports_url + 'users.<format>', **reports_kwargs)
def report_users_data(board, conversation, format):
    assure_correct_board(conversation, board)
    return report_routes.users_data(conversation, format)


@urlpatterns.route(reports_url + 'comments.<format>', **reports_kwargs)
def report_comments_data(board, conversation, format):
    assure_correct_board(conversation, board)
    return report_routes.comments_data(conversation, format)


#
# Utility functions
#
def assure_correct_board(conversation, board):
    """
    Raise 404 if conversation does not belong to board.
    """
    if not board.has_conversation(conversation):
        raise Http404
    conversation.board = board


def get_conversation_detail_context(request, conversation):
    """
    Common implementation used by both /conversations/<slug> and inside boards
    in /<board>/conversations/<slug>/
    """
    user = request.user
    is_favorite = user.is_authenticated and conversation.favorites.filter(user=user).exists()
    comment_form = CommentForm(None, conversation=conversation)
    voted = False
    if user.is_authenticated:
        voted = Vote.objects.filter(author=user).exists()

    # User is voting in the current comment. We still need to choose a random
    # comment to display next.
    if request.POST.get('action') == 'vote':
        vote = request.POST['vote']
        comment_id = request.POST['comment_id']
        Comment.objects.get(id=comment_id).vote(user, vote)
        log.info(f'user {user.id} voted {vote} on comment {comment_id}')

    # User is posting a new comment. We need to validate the form and try to
    # keep the same comment that was displayed before.
    elif request.POST.get('action') == 'comment':
        comment_form = CommentForm(request.POST, conversation=conversation)
        if comment_form.is_valid():
            new_comment = comment_form.cleaned_data['content']
            new_comment = conversation.create_comment(user, new_comment)
            comment_form = CommentForm(conversation=conversation)
            log.info(f'user {user.id} posted comment {new_comment.id} on {conversation.id}')

    # User toggled the favorite status of conversation.
    elif request.POST.get('action') == 'favorite':
        conversation.toggle_favorite(user)
        log.info(f'user {user.id} toggled favorite status of conversation {conversation.id}')

    # User to pass modalities
    elif request.POST.get('modalities') == 'pass':
        voted = True

    # User is probably trying to something nasty ;)
    elif request.method == 'POST':
        log.warning(f'user {user.id} se nt invalid POST request: {request.POST}')
        return HttpResponseServerError('invalid action')

    n_comments_under_moderation = rules.compute('ej_conversations.comments_under_moderation', conversation, user)
    comments_made = rules.compute('ej_conversations.comments_made', conversation, user)

    return {
        # Objects
        'conversation': conversation,
        'comment': conversation.next_comment(user, None),
        'comment_form': comment_form,

        # Statistics
        'n_voted': conversation.votes.filter(author=user).count() if user.is_authenticated else 0,
        'total_comments': conversation.comments.approved().count(),

        # Permissions and predicates
        'is_favorite': is_favorite,
        'can_comment': user.is_authenticated,
        'can_edit': user.has_perm('ej.can_edit_conversation', conversation),
        'cannot_comment_reason': '',
        'comments_under_moderation': n_comments_under_moderation,
        'comments_made': comments_made,
        'max_comments': max_comments_per_conversation(),
        'user_is_owner': conversation.author == user,
        'voted': voted,
        'board_palette': conversation.css_palette
    }


def get_conversation_edit_context(request, conversation, board=None):
    if request.method == 'POST':
        form = forms.ConversationForm(
            data=request.POST,
            instance=conversation,
        )
        if form.is_valid():
            form.save()
            return redirect(conversation.get_absolute_url() + 'moderate/')
    else:
        form = forms.ConversationForm(instance=conversation)
    tags = list(map(str, conversation.tags.all()))

    return {
        'form': form,
        'conversation': conversation,
        'tags': ",".join(tags),
        'can_promote_conversation': request.user.has_perm('can_publish_promoted'),
        'comments': list(conversation.comments.filter(status='pending')),
        'board': board,
    }
