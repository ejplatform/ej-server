from logging import getLogger

from boogie.models import F
from boogie.router import Router
from django.db import transaction
from django.http import HttpResponse, HttpResponseServerError, HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from hyperpython import a

from ej_boards.models import Board
from ej_users.models import SignatureFactory

from . import forms, models
from .models import Conversation
from .rules import next_comment
from .utils import (
    check_promoted,
    conversation_admin_menu_links,
    handle_detail_favorite,
    handle_detail_comment,
    handle_detail_vote,
)

log = getLogger("ej")

app_name = "ej_conversations"
urlpatterns = Router(
    template="ej_conversations/{name}.jinja2", models={"conversation": models.Conversation}
)
conversation_url = f"<model:conversation>/<slug:slug>/"


#
# Display conversations
#
@urlpatterns.route("", name="list")
def list_view(
    request,
    queryset=Conversation.objects.filter(is_promoted=True),
    context=None,
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

    return {
        "conversations": queryset,
        "title": _(title),
        "subtitle": _("Participate voting and creating comments!"),
        "board": None,
        "help_title": help_title,
        "conversations_limit": max_conversation_per_user,
        **(context or {"user_boards": user_boards}),
    }


@urlpatterns.route(conversation_url, login=True)
def detail(request, conversation, slug=None, check=check_promoted):
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

    return {
        "conversation": conversation,
        "comment": conversation.next_comment_with_id(user, comment_id),
        "menu_links": conversation_admin_menu_links(conversation, user),
        "comment_form": form,
        **ctx,
    }


#
# Admin URLs
#
@urlpatterns.route("add/", perms=["ej.can_promote_conversations"])
def create(request, context=None, **kwargs):
    kwargs.setdefault("is_promoted", True)
    user = request.user
    form = forms.ConversationForm(request=request)
    if form.is_valid_post() and request.user.has_perm("ej.can_add_conversation"):
        with transaction.atomic():
            conversation = form.save_comments(request.user, **kwargs)
        return redirect(conversation.url("report:general-report"))
    return {
        "form": form,
        **(context or {"board": None, "user_boards": Board.objects.filter(owner=user)}),
    }  # TODO /conversation/add está funcionando para o admin, por isso foi preciso setar o board: None


@urlpatterns.route(conversation_url + "edit/", perms=["ej.can_edit_conversation:conversation"])
def edit(request, conversation, slug=None, check=check_promoted, **kwargs):
    check(conversation, request)
    form = forms.ConversationForm(request=request, instance=conversation)
    can_publish = request.user.has_perm("ej_conversations.can_publish_promoted")
    is_promoted = conversation.is_promoted

    if form.is_valid_post():
        # Check if user is not trying to edit the is_promoted status without
        # permission. This is possible since the form sees this field
        # for all users and does not check if the user is authorized to
        # change is value.
        new = form.save(**kwargs)
        if new.is_promoted != is_promoted:
            new.is_promoted = is_promoted
            new.save()

        # Now we decide the correct redirect page
        page = request.POST.get("next")
        if page == "stereotypes":
            url = conversation.url("cluster:stereotype-votes")
        elif page == "moderate":
            url = conversation.url("conversation:moderate")
        elif conversation.is_promoted:
            url = conversation.get_absolute_url()
        else:
            url = conversation.url("conversation:list")
        return redirect(url)

    return {
        "conversation": conversation,
        "form": form,
        "menu_links": conversation_admin_menu_links(conversation, request.user),
        "can_publish": can_publish,
    }


@urlpatterns.route(conversation_url + "moderate/", perms=["ej.can_moderate_conversation:conversation"])
def moderate(request, conversation, slug=None, check=check_promoted):
    check(conversation, request)
    form = forms.ModerationForm(request=request)

    if form.is_valid_post():
        form.save()
        form = forms.ModerationForm(user=request.user)

    # Fetch all comments and filter
    status_filter = lambda value: lambda x: x.status == value
    status = models.Comment.STATUS
    comments = conversation.comments.annotate(annotation_author_name=F.author.name)

    return {
        "conversation": conversation,
        "approved": list(filter(status_filter(status.approved), comments)),
        "pending": list(filter(status_filter(status.pending), comments)),
        "rejected": list(filter(status_filter(status.rejected), comments)),
        "menu_links": conversation_admin_menu_links(conversation, request.user),
        "form": form,
    }


def login_link(content, obj):
    path = obj.get_absolute_url()
    return a(content, href=reverse("auth:login") + f"?next={path}")
