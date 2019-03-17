from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from hyperpython import a
from hyperpython.django import csrf_input

from ej.roles import with_template
from .. import models
from ..enums import RejectionReason
from ..routes_comments import comment_url


@with_template(models.Comment, role='card')
def comment_card(comment, request=None, target=None, show_actions=None, **kwargs):
    """
    Render comment information inside a comment card.
    """

    user = getattr(request, 'user', None)
    is_authenticated = getattr(user, 'is_authenticated', False)

    if is_authenticated:
        login_anchor = None
    else:
        login = reverse('auth:login')
        login_anchor = a(_('login'), href=f'{login}?next={comment.conversation.get_absolute_url()}')

    buttons = {
        'disagree': ('fa-times', 'text-negative', _('Disagree')),
        'skip': ('fa-arrow-right', 'text-black', _('Skip')),
        'agree': ('fa-check', 'text-positive', _('Agree')),
    }

    return {
        'author': comment.author.username,
        'comment': comment,
        'show_actions': is_authenticated,
        'csrf_input': csrf_input(request),
        'buttons': buttons,
        'login_anchor': login_anchor,
        'target': target,
        **kwargs
    }


@with_template(models.Comment, role='moderate')
def comment_moderate(comment, request=None, **kwargs):
    """
    Render a comment inside a moderation card.
    """

    return {
        'created': comment.created,
        'author': comment.author_name,
        'text': comment.content,
    }


@with_template(models.Comment, role='reject-reason')
def comment_reject_reason(comment, **kwargs):
    """
    Show reject reason for each comment.
    """

    rejection_reason = comment.rejection_reason_text
    if comment.status != comment.STATUS.rejected:
        rejection_reason = None
    elif comment.rejection_reason != RejectionReason.USER_PROVIDED:
        rejection_reason = comment.rejection_reason.description

    return {
        'comment': comment,
        'conversation_url': comment.conversation.get_absolute_url(),
        'status': comment.status,
        'status_name': dict(models.Comment.STATUS)[comment.status].capitalize(),
        'rejection_reason': rejection_reason
    }


@with_template(models.Comment, role='summary')
def comment_summary(comment, **kwargs):
    """
    Show comment summary.
    """
    return {
        'created': comment.created,
        'tag': _('Comment'),
        'tag_link': comment_url(comment),
        'text': comment.content,
        'agree': comment.agree_count,
        'skip': comment.skip_count,
        'disagree': comment.disagree_count,
    }
