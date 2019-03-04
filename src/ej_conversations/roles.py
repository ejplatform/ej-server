from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from hyperpython import a, html, Text
from hyperpython.django import csrf_input

from boogie import rules
from ej.roles import with_template, extra_content, progress_bar
from . import models


def get_annotation(obj, annotation, fallback):
    attr = f'annotation_{annotation}'
    if hasattr(obj, attr):
        return getattr(obj, attr)
    else:
        return fallback()


# ------------------------------------------------------------------------------
# Conversation
# ------------------------------------------------------------------------------

@with_template(models.Conversation, role='card')
def conversation_card(conversation, url=None, **kwargs):
    """
    Render a round card representing a conversation in a list.
    """

    tag = conversation.tags.first()  # only first is shown in card to prevent overflow
    return {
        'author': conversation.author.name,
        'conversation': conversation,
        'url': url or conversation.get_absolute_url(),
        'tag': tag,
        'n_comments': conversation.approved_comments.count(),
        'n_votes': conversation.votes.count(),
        'n_favorites': conversation.favorites.count(),
        'conversation_modifiers': '',
        **kwargs,
    }


@with_template(models.Conversation, role='balloon')
def conversation_balloon(conversation, request=None, actions=None,
                         is_favorite=False, **kwargs):
    """
    Render details of a conversation inside a conversation balloon.
    """

    user = getattr(request, 'user', None)

    # Share and favorite actions bellow the balloon
    if actions is not False:
        is_authenticated = getattr(user, 'is_authenticated', False)
        is_favorite = is_authenticated and conversation.is_favorite(user)
        if actions is None:
            actions = is_authenticated

    return {
        'conversation': conversation,
        'user': user,
        'tags': list(conversation.tags.values_list('name', flat=True)),
        'is_favorite': is_favorite,
        'actions': actions,
    }


@with_template(models.Conversation, role='comment-form')
def comment_form(conversation, request=None, content=None, user=None, **kwargs):
    """
    Render comment form for conversation.
    """
    # Check user credentials
    user = user or getattr(request, 'user', None)
    if not user.is_authenticated:
        conversation_url = conversation.get_absolute_url()
        login = reverse('auth:login')
        return {
            'user': None,
            'login_anchor': a(_('login'), href=f'{login}?next={conversation_url}')
        }

    # Check if user still have comments left
    n_comments = rules.compute('ej.remaining_comments', conversation, user)
    if conversation.author != user and n_comments == 0:
        return {'comments_exceeded': True}

    # Everything is ok, proceed ;)
    return {
        'user': user,
        'csrf_input': csrf_input(request),
        'n_comments': n_comments,
        'content': content,
    }


@html.register(models.Conversation, role='ask-create-comment')
def comment_statistics(conversation, request=None, **kwargs):
    """
    Render comment form for one conversation.
    """
    n_moderation = 0
    n_comments = 0
    max_comments = 3
    moderation_msg = _('{n} awaiting moderation').format(n=n_moderation)
    comments_count = _('{ratio} comments').format(
        ratio=f'<strong>{n_comments}</strong> / {max_comments}'
    )
    return extra_content(_('Create comment'), Text(
        f'{comments_count}'
        f'<div class="text-7 strong">{moderation_msg}</div>',
        escape=False
    ), icon='plus')


@html.register(models.Conversation, role='ask-opinion-groups')
def opinion_group(conversation, request=None, **kwargs):
    """
    Render comment form for one conversation.
    """
    n_groups = 3
    group_id = 2
    msg = _('This conversation has {n_groups} groups, '
            'and you are in group {group_id}.').format(n_groups=n_groups,
                                                       group_id=group_id)
    return extra_content(_('Opinion groups'), msg, icon='chart-pie')


@html.register(models.Conversation, role='user-progress')
def user_progress(conversation, request=None, user=None):
    """
    Render comment form for one conversation.
    """
    user = user or request.user
    n = get_annotation(
        conversation, 'user_votes',
        lambda: user.votes.filter(comment__conversation=conversation).count()
    )
    total = get_annotation(
        conversation, 'approved_comments',
        lambda: conversation.comments.approved().count()
    )
    n = min(n, total)
    return progress_bar(n, total)


@with_template(models.Conversation, role='summary')
def conversation_summary(conversation, request=None):
    """
    Show only essential information about a conversation.
    """

    # Optimized tag
    tag = get_annotation(
        conversation, 'tag_first',
        lambda: conversation.tags.first())

    return {
        'text': conversation.text,
        'tag': tag or _('Conversation'),
        'created': conversation.created,
    }


# ------------------------------------------------------------------------------
# Comments
# ------------------------------------------------------------------------------

@with_template(models.Comment, role='card')
def comment_card(comment, request=None, **kwargs):
    """
    Render comment information inside a comment card.
    """

    user = getattr(request, 'user', None)
    is_authenticated = getattr(user, 'is_authenticated', False)

    login = reverse('auth:login')
    comment_url = comment.conversation.get_absolute_url()
    login_anchor = a(_('login'), href=f'{login}?next={comment_url}')
    buttons = {
        'disagree': ('fa-times', 'text-negative', _('Disagree')),
        'skip': ('fa-arrow-right', '', _('Skip')),
        'agree': ('fa-check', 'text-positive', _('Agree')),
    }
    return {
        'author': comment.author.name,
        'comment': comment,
        'rejection_reasons': dict(models.Comment.REJECTION_REASON),
        'show_actions': is_authenticated,
        'csrf_input': csrf_input(request),
        'buttons': buttons,
        'login_anchor': login_anchor,
        **kwargs,
    }


@with_template(models.Comment, role='moderate')
def comment_moderate(comment, request=None, **kwargs):
    """
    Render a comment inside a moderation card.
    """

    return {
        'created': comment.created,
        'author': get_annotation(comment, 'author_name',
                                 lambda: comment.author.name),
        'text': comment.content,
        # 'rejection_reasons': dict(models.Comment.REJECTION_REASON),
    }


@with_template(models.Comment, role='summary')
def comment_summary(comment, **kwargs):
    """
    Show comment summary.
    """
    return {
        'created': comment.created,
        'tag': _('Comment'),
        'text': comment.content,
        'agree': comment.agree_count,
        'skip': comment.skip_count,
        'disagree': comment.disagree_count,
    }


@with_template(models.Comment, role='reject-reason')
def comment_reject_reason(comment, **kwargs):
    """
    Show reject reason for each comment.
    """

    rejection_reason = comment.rejection_reason
    if rejection_reason in dict(models.Comment.REJECTION_REASON) and comment.status == comment.STATUS.rejected:
        rejection_reason = dict(models.Comment.REJECTION_REASON)[comment.rejection_reason]
    else:
        rejection_reason = None
    return {
        'rejection_reasons': dict(models.Comment.REJECTION_REASON),
        'comment': comment,
        'conversation_url': comment.conversation.get_absolute_url(),
        'status': comment.status,
        'status_name': dict(models.Comment.STATUS)[comment.status].capitalize(),
        'rejection_reason': rejection_reason
    }
