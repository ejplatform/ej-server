from boogie import rules
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from hyperpython import a, html, Blob, div
from hyperpython.django import csrf_input

from ej.roles import with_template, progress_bar
from ..rules import max_comments_per_conversation
from .. import forms
from .. import models


@with_template(models.Conversation, role="balloon")
def conversation_balloon(
    conversation, request=None, actions=None, is_favorite=False, **kwargs
):
    """
    Render details of a conversation inside a conversation balloon.
    """

    user = getattr(request, "user", None)

    # Share and favorite actions bellow the balloon
    if actions is not False:
        is_authenticated = getattr(user, "is_authenticated", False)
        is_favorite = is_authenticated and conversation.is_favorite(user)
        if actions is None:
            actions = is_authenticated

    return {
        "text": conversation.text,
        "user": user,
        "tags": conversation.tag_names,
        "hidden": conversation.is_hidden,
        "is_favorite": is_favorite,
        "actions": actions,
    }


@with_template(models.Conversation, role="card")
def conversation_card(conversation, url=None, request=None, text=None, hidden=None):
    """
    Render a round card representing a conversation in a list.
    """

    return {
        "author": conversation.author_name,
        "text": text or conversation.text,
        "progress": conversation_user_progress(conversation, request=request),
        "hidden": conversation.is_hidden if hidden is None else hidden,
        "url": url or conversation.get_absolute_url(),
        "tag": conversation.first_tag,
        "n_comments": conversation.n_comments,
        "n_votes": conversation.n_votes,
        "n_favorites": conversation.n_favorites,
    }


@with_template(models.Conversation, role="comment-form")
def conversation_comment_form(
    conversation, request=None, content=None, user=None, form=None, target=None
):
    """
    Render comment form for conversation.
    """
    # Check user credentials
    user = user or getattr(request, "user", None)
    if not user.is_authenticated:
        conversation_url = conversation.get_absolute_url()
        login = reverse("auth:login")
        return {
            "user": None,
            "login_anchor": a(_("login"), href=f"{login}?next={conversation_url}"),
        }

    # Check if user still have comments left
    n_comments = rules.compute("ej.remaining_comments", conversation, user)
    if conversation.author != user and n_comments <= 0:
        return {"comments_exceeded": True, "user": user}

    # Everything is ok, proceed ;)
    return {
        "user": user,
        "csrf_input": csrf_input(request),
        "n_comments": n_comments,
        "content": content,
        "target": target or "main",
        "form": form or forms.CommentForm(request=request, conversation=conversation),
    }


@html.register(models.Conversation, role="create-comment")
def conversation_create_comment(conversation, request=None, **kwargs):
    """
    Render "create comment" button for one conversation.
    """
    conversation.set_request(request)
    n_comments = conversation.n_user_comments
    n_moderation = conversation.n_pending_comments
    max_comments = max_comments_per_conversation()
    moderation_msg = _("{n} awaiting moderation").format(n=n_moderation)
    comments_count = _("{ratio} comments").format(
        ratio=f"<strong>{n_comments}</strong> / {max_comments}"
    )

    # FIXME: Reactivate when full UI for the comment form is implemented
    # return extra_content(
    #     _("Create comment"),
    #     Blob(f"{comments_count}" f'<div class="text-7 strong">{moderation_msg}</div>'),
    #     icon="plus",
    #     id="create-comment",
    # )
    return div(
        Blob(f"{comments_count}" f'<div class="text-7 strong">{moderation_msg}</div>'),
        id="create-comment",
        class_="extra-content",
    )


@html.register(models.Conversation, role="detail-page-extra")
def conversation_detail_page_extra(conversation, **kwargs):
    return ""


@with_template(models.Conversation, role="summary")
def conversation_summary(conversation, request=None):
    """
    Show only essential information about a conversation.
    """

    return {
        "text": conversation.text,
        "tag": conversation.first_tag or _("Conversation"),
        "created": conversation.created,
    }


@html.register(models.Conversation, role="user-progress")
def conversation_user_progress(conversation, request=None, user=None):
    """
    Render comment form for one conversation.
    """

    user = user or request.user
    conversation.for_user = user
    n = conversation.n_user_votes
    total = conversation.n_comments
    return progress_bar(min(n, total), total)
