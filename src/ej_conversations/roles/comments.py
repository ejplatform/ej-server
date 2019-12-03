from django.apps import apps
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from hyperpython import a, html
from hyperpython.django import csrf_input

from ej.roles import with_template
from .. import models
from ..enums import RejectionReason
from ..models import Comment
from ..routes_comments import comment_url

HAS_GAMIFICATION = apps.is_installed("ej_gamification")


@with_template(Comment, role="card")
def comment_card(comment: Comment, request=None, target=None, show_actions=None, **kwargs):
    """
    Render comment information inside a comment card.
    """

    login_anchor, is_authenticated, user = authenticate_user()
    badge, buttons = gamification(user, comment)

    return {
        "author": comment.author.username,
        "comment": comment,
        "show_actions": is_authenticated,
        "csrf_input": csrf_input(request),
        "buttons": buttons,
        "login_anchor": login_anchor,
        "target": target,
        "badge": badge,
        **kwargs,
    }

def authenticate_user():

    user = getattr(request, "user", None)
    is_authenticated = getattr(user, "is_authenticated", False)

    if is_authenticated:
        login_anchor = None
    else:
        login = reverse("auth:login")
        login_anchor = a(_("login"), href=f"{login}?next={comment.conversation.get_absolute_url()}")

    return login_anchor, is_authenticated, user

def gamify(user, comment):
    badge = ""
    if HAS_GAMIFICATION:
        from ej_gamification import get_participation

        level = get_participation(user, comment.conversation).voter_level
        badge = html(level, role="stars")

    buttons = {
        "disagree": ("fa-times", "text-negative", _("Disagree")),
        "skip": ("fa-arrow-right", "text-black", _("Skip")),
        "agree": ("fa-check", "text-positive", _("Agree")),
    }

    return badge, buttons



@with_template(Comment, role="moderate")
def comment_moderate(comment: Comment, request=None, **kwargs):
    """
    Render a comment inside a moderation card.
    """

    moderator = getattr(comment.moderator, "name", None)
    return {
        "created": comment.created,
        "author": comment.author_name,
        "text": comment.content,
        "moderator": moderator,
    }


@with_template(Comment, role="reject-reason")
def comment_reject_reason(comment: Comment, **kwargs):
    """
    Show reject reason for each comment.
    """

    rejection_reason = comment.rejection_reason_text
    if comment.status != comment.STATUS.rejected:
        rejection_reason = None
    elif comment.rejection_reason != RejectionReason.USER_PROVIDED:
        rejection_reason = comment.rejection_reason.description

    return {
        "comment": comment,
        "conversation_url": comment.conversation.get_absolute_url(),
        "status": comment.status,
        "status_name": dict(models.Comment.STATUS)[comment.status].capitalize(),
        "rejection_reason": rejection_reason,
    }


@with_template(Comment, role="summary")
def comment_summary(comment: Comment, **kwargs):
    """
    Show comment summary.
    """
    return {
        "created": comment.created,
        "tag": _("Comment"),
        "tag_link": comment_url(comment),
        "text": comment.content,
        "agree": comment.agree_count,
        "skip": comment.skip_count,
        "disagree": comment.disagree_count,
    }

@with_template(Comment, role="stats", template="ej/role/voting-stats.jinja2")
def comment_stats(comment: Comment, request=None):
    return {
        "agree": comment.agree_count,
        "skip": comment.skip_count,
        "disagree": comment.disagree_count,
        "request": request,
    }
