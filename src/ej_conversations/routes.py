from logging import getLogger

from django.db import transaction
from django.http import Http404, HttpResponseServerError
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from hyperpython import a

from boogie import rules
from boogie.router import Router
from . import forms, models
from .forms import CommentForm
from .models import Conversation, Comment, Vote
from .rules import max_comments_per_conversation

log = getLogger('ej')

app_name = 'ej_conversations'
urlpatterns = Router(
    template=['ej_conversations/{name}.jinja2', 'generic.jinja2'],
    models={
        'conversation': models.Conversation,
        'comment': models.Comment,
    },
    lookup_field={
        'conversation': 'slug',
        'comment': 'slug',
    },
    lookup_type='slug',
)
conversation_url = f'<model:conversation>/'


#
# Admin URLs
#
@urlpatterns.route('add/', perms=['ej.can_add_promoted_conversation'])
def create(request):
    form = forms.ConversationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            conversation = form.save_all(
                author=request.user,
                is_promoted=True,
            )
        return redirect(conversation.get_absolute_url() + 'stereotypes/')
    return {'form': form}


@urlpatterns.route(conversation_url + 'edit/',
                   perms=['ej.can_edit_conversation:conversation'])
def edit(request, conversation):
    if not conversation.is_promoted:
        raise Http404
    return get_conversation_edit_context(request, conversation)


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


@urlpatterns.route(conversation_url + 'moderate/',
                   perms=['ej.can_moderate_conversation:conversation'])
def moderate(request, conversation):
    if not conversation.is_promoted:
        raise Http404
    return get_conversation_moderate_context(request, conversation)


def get_conversation_moderate_context(request, conversation):
    if request.method == 'POST':
        comment = models.Comment.objects.get(id=request.POST['comment'])
        if request.POST['vote'] == 'approve':
            comment.status = comment.STATUS.approved
            comment.rejection_reason = ''
        elif request.POST['vote'] == 'disapprove':
            comment.status = comment.STATUS.rejected
            comment.rejection_reason = request.POST['rejection_reason']
        else:
            # User is probably trying to something nasty ;)
            log.warning(f'user {request.user.id} sent invalid POST request: {request.POST}')
            return HttpResponseServerError('invalid action')
        comment.save()

    status = request.GET.get('status', 'pending')
    tags = list(map(str, conversation.tags.all()))

    return {
        'conversation': conversation,
        'comment_status': status,
        'comments': list(conversation.comments.filter(status=status)),
        'tags': tags,
    }


#
# Display conversations
#
@urlpatterns.route('', name='list')
def conversation_list(request):
    show_welcome_window = 'show_welcome_window' in request.COOKIES.keys()
    ctx = {
        'conversations': Conversation.objects.filter(is_promoted=True, is_hidden=False),
        'can_add_conversation': request.user.has_perm('ej.can_add_promoted_conversation'),
        'create_url': reverse('conversation:create'),
        'topic': _('A space for adolescents to discuss actions that promote, guarantee and defend their rights'),
        'title': _('Public conversations'),
        'subtitle': _('Participate of conversations and give your opinion with comments and votes!'),
        'description': _('Participate of conversations and give your opinion with comments and votes!'),
        'show_welcome_window': show_welcome_window,
        'board_palette': Conversation.get_default_css_palette()
    }
    response = render(request, 'ej_conversations/list.jinja2', ctx)
    if (show_welcome_window):
        response.delete_cookie('show_welcome_window')
    return response


@urlpatterns.route(conversation_url)
def detail(request, conversation):
    if not conversation.is_promoted:
        raise Http404
    return get_conversation_detail_context(request, conversation)


def get_conversation_detail_context(request, conversation):
    """
    Common implementation used by both /conversations/<slug> and inside boards
    in /<board>/conversations/<slug>/
    """
    user = request.user
    is_favorite = user.is_authenticated and conversation.followers.filter(user=user).exists()
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


#
# Display details about comments
#
@urlpatterns.route(conversation_url + 'comments/')
def comment_list(request, conversation):
    if not conversation.is_promoted:
        raise Http404

    user = request.user
    comments = conversation.comments.filter(author=user)
    n_comments = rules.compute('ej.remaining_comments', conversation, user)
    return {
        'content_title': _('List conversations'),
        'conversation': conversation,
        'approved': comments.approved(),
        'rejected': comments.rejected(),
        'pending': comments.pending(),
        'remaining_comments': n_comments,
        'can_comment': user.has_perm('ej.can_comment', conversation),
        'can_edit': user.has_perm('ej.can_edit_conversation', conversation),
    }


@urlpatterns.route(conversation_url + 'comments/<model:comment>/', lookup_field={'comment': 'pk'})
def comment_detail(conversation, comment):
    if not conversation.is_promoted:
        raise Http404

    return {
        'conversation': conversation,
        'comment': comment,
    }


#
# Auxiliary functions
#
def login_link(content, obj):
    path = obj.get_absolute_url()
    return a(content, href=reverse('auth:login') + f'?next={path}')
