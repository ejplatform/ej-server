from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from hyperpython import a, html, Text
from hyperpython.django import csrf_input

from boogie import rules
from ej.roles import with_template, extra_content, progress_bar
from ej_conversations.routes_comments import comment_url
from . import models


# ------------------------------------------------------------------------------
# Conversation
# ------------------------------------------------------------------------------

@with_template(models.Conversation, role='card')
def conversation_card(conversation, url=None, request=None):
    """
    Render a round card representing a conversation in a list.
    """

    return {
        'author': conversation.author_name,
        'conversation': conversation,
        'url': url or conversation.get_absolute_url(),
        'tag': conversation.first_tag,
        'n_comments': conversation.n_comments,
        'n_votes': conversation.n_votes,
        'n_favorites': conversation.n_favorites,
        'conversation_modifiers': '',
        'request': request,
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
        'text': conversation.text,
        'user': user,
        'tags': conversation.tag_names,
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
    conversation.for_user = user
    n = conversation.n_user_votes
    total = conversation.n_comments
    return progress_bar(min(n, total), total)


@with_template(models.Conversation, role='summary')
def conversation_summary(conversation, request=None):
    """
    Show only essential information about a conversation.
    """

    return {
        'text': conversation.text,
        'tag': conversation.first_tag or _('Conversation'),
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
        'skip': ('fa-arrow-right', 'text-black', _('Skip')),
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
        'author': comment.author_name,
        'text': comment.content,
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
