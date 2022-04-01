from logging import getLogger

from django.db import transaction
from django.db.models import F
from django.http import HttpResponseServerError
from django.urls import reverse
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from hyperpython import a
from django.contrib.auth.decorators import login_required

from ej_boards.models import Board
from ej_users.models import SignatureFactory

from . import forms, models
from .models import Conversation
from .utils import (
    check_promoted,
    conversation_admin_menu_links,
    handle_detail_favorite,
    handle_detail_comment,
    handle_detail_vote,
)

from ej.decorators import (
    can_add_conversations,
    can_edit_conversation,
    can_moderate_conversation,
    can_acess_list_view,
)

log = getLogger("ej")

#
# Display conversations
#
def public_list_view(
    request,
    queryset=Conversation.objects.filter(is_promoted=True),
    title=_("Public conversations"),
    help_title="",
):
    user = request.user
    user_boards = []
    if not (user.is_staff or user.is_superuser or user.has_perm("ej_conversations.can_publish_promoted")):
        queryset = queryset.filter(is_hidden=False)

    annotations = ("n_votes", "n_comments", "n_user_votes", "first_tag", "n_favorites", "author_name")
    queryset = queryset.cache_annotations(*annotations, user=user).order_by("-created")
    if user.is_authenticated:
        user_signature = SignatureFactory.get_user_signature(request.user)
        max_conversation_per_user = user_signature.get_conversation_limit()
        user_boards = Board.objects.filter(owner=user)
    else:
        max_conversation_per_user = 0

    render_context = {
        "conversations": queryset,
        "title": _(title),
        "subtitle": _("Participate voting and creating comments!"),
        "board": None,
        "help_title": help_title,
        "conversations_limit": max_conversation_per_user,
        "user_boards": user_boards,
    }
    return render(request, "ej_conversations/list.jinja2", render_context)


@login_required
@can_acess_list_view
def list_view(
    request,
    board_slug,
):
    user = request.user
    user_boards = Board.objects.filter(owner=user)
    board = Board.objects.get(slug=board_slug)
    queryset = board.conversations.annotate_attr(board=board)

    help_title = (
        _(
            "Welcome to EJ. This is your personal board. Board is where your conversations will be available. Press 'New conversation' to starts collecting yours audience opinion."
        ),
    )

    if not user.get_profile().completed_tour:
        return redirect(f"{board.get_absolute_url()}tour")

    if not (user.is_staff or user.is_superuser or user.has_perm("ej_conversations.can_publish_promoted")):
        queryset = queryset.filter(is_hidden=False)

    annotations = ("n_votes", "n_comments", "n_user_votes", "first_tag", "n_favorites", "author_name")
    queryset = queryset.cache_annotations(*annotations, user=user).order_by("-created")

    user_signature = SignatureFactory.get_user_signature(user)
    max_conversation_per_user = user_signature.get_conversation_limit()

    render_context = {
        "conversations": queryset,
        "title": _(board.title),
        "subtitle": _("Participate voting and creating comments!"),
        "help_title": help_title,
        "conversations_limit": max_conversation_per_user,
        "board": board,
        "user_boards": user_boards,
    }
    return render(request, "ej_conversations/conversation-list.jinja2", render_context)


@login_required
def detail(request, conversation_id, slug, board_slug, check=check_promoted):
    conversation = Conversation.objects.get(id=conversation_id)
    check(conversation, request)
    user = request.user
    form = forms.CommentForm(conversation=conversation)
    comment_id = request.GET.get("comment_id")
    ctx = {}

    if request.method == "POST":
        action = request.POST["action"]

        if action == "vote":
            ctx = handle_detail_vote(request)
        elif action == "comment":
            ctx = handle_detail_comment(request, conversation)
        elif action == "favorite":
            ctx = handle_detail_favorite(request, conversation)
        else:
            log.warning(f"user {request.user.id} se nt invalid POST request: {request.POST}")
            return HttpResponseServerError("invalid action")

    context = {
        "conversation": conversation,
        "comment": conversation.next_comment_with_id(user, comment_id),
        "menu_links": conversation_admin_menu_links(conversation, user),
        "comment_form": form,
        **ctx,
    }
    return render(request, "ej_conversations/conversation-detail.jinja2", context)


# @can_edit_board TODO: criar um can_edit_board
@login_required
@can_add_conversations
@can_acess_list_view
def create(request, board_slug, context=None, **kwargs):
    user = request.user
    board = Board.objects.get(slug=board_slug)
    kwargs.setdefault("is_promoted", True)
    kwargs["board"] = board
    user_boards = Board.objects.filter(owner=user)
    form = forms.ConversationForm(request=request)
    if form.is_valid_post():
        with transaction.atomic():
            conversation = form.save_comments(user, **kwargs)
        return redirect(conversation.url("dataviz:dashboard"))

    context = {
        "form": form,
        "board": board,
        "user_boards": user_boards,
    }

    return render(request, "ej_conversations/conversation-create.jinja2", context)


@login_required
@can_edit_conversation
def edit(request, conversation_id, slug, board_slug, **kwargs):
    conversation = Conversation.objects.get(id=conversation_id)
    board = Board.objects.get(slug=board_slug)
    form = forms.ConversationForm(request=request, instance=conversation)
    can_publish = request.user.has_perm("ej_conversations.can_publish_promoted")
    is_promoted = conversation.is_promoted

    if form.is_valid_post():
        # Check if user is not trying to edit the is_promoted status without
        # permission. This is possible since the form sees this field
        # for all users and does not check if the user is authorized to
        # change is value.
        new = form.save(board=board, **kwargs)
        if new.is_promoted != is_promoted:
            new.is_promoted = is_promoted
            new.save()

        # Now we decide the correct redirect page
        page = request.POST.get("next")
        if page == "stereotypes":
            url = conversation.url("cluster:stereotype-votes")
        elif page == "moderate":
            url = conversation.patch_url("conversation:moderate")
        elif conversation.is_promoted:
            url = conversation.get_absolute_url()
        else:
            url = conversation.patch_url("conversation:list")
        return redirect(url)

    context = {
        "conversation": conversation,
        "form": form,
        "menu_links": conversation_admin_menu_links(conversation, request.user),
        "can_publish": can_publish,
        "board": board,
    }
    return render(request, "ej_conversations/conversation-edit.jinja2", context)


@login_required
@can_edit_conversation
@can_moderate_conversation
def moderate(request, conversation_id, slug, board_slug):
    conversation = Conversation.objects.get(id=conversation_id)
    form = forms.ModerationForm(request=request)

    if form.is_valid_post():
        form.save()
        form = forms.ModerationForm(user=request.user)

    # Fetch all comments and filter
    status_filter = lambda value: lambda x: x.status == value
    status = models.Comment.STATUS
    comments = conversation.comments.annotate(annotation_author_name=F("author__name"))

    context = {
        "conversation": conversation,
        "approved": list(filter(status_filter(status.approved), comments)),
        "pending": list(filter(status_filter(status.pending), comments)),
        "rejected": list(filter(status_filter(status.rejected), comments)),
        "menu_links": conversation_admin_menu_links(conversation, request.user),
        "form": form,
    }
    return render(request, "ej_conversations/conversation-moderate.jinja2", context)


def login_link(content, obj):
    path = obj.get_absolute_url()
    return a(content, href=reverse("auth:login") + f"?next={path}")
