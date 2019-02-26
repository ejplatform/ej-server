from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from hyperpython import a, html, Text
from hyperpython.django import csrf_input

from boogie import rules
from ej.roles import with_template, extra_content
from ej_boards.models import BoardSubscription
from . import models


#
# Conversation roles
#
@with_template(models.Conversation, role='card')
def conversation_card(conversation, request=None, url=None, **kwargs):
    """
    Render a round card representing a conversation in a list.
    """

    user = getattr(request, 'user', None)
    moderate_url = None
    can_moderate = user.has_perm('ej.can_moderate_conversation', conversation)
    if can_moderate:
        moderate_url = reverse('conversation:moderate', kwargs={'conversation': conversation})
    tag = conversation.tags.first()  # only first is shown in card to prevent overflow
    subscription = BoardSubscription.objects.filter(conversation=conversation)
    board = None
    if subscription.exists():
        board = subscription[0].board
    return {
        'author': conversation.author.name,
        'conversation': conversation,
        'url': url or conversation.get_absolute_url(board),
        'tag': tag,
        'n_comments': conversation.approved_comments.count(),
        'n_votes': conversation.votes.count(),
        'n_followers': conversation.followers.count(),
        'user_can_moderate': can_moderate,
        'moderate_url': moderate_url,
        'conversation_modifiers': '',
        **kwargs,
    }


@with_template(models.Conversation, role='balloon')
def conversation_balloon(conversation, request=None, **kwargs):
    """
    Render details of a conversation inside a conversation balloon.
    """

    user = getattr(request, 'user', None)
    favorites = models.FavoriteConversation.objects
    is_authenticated = getattr(user, 'is_authenticated', False)
    is_favorite = is_authenticated and conversation.is_favorite(user)
    tags = list(map(str, conversation.tags.all()))

    return {
        'conversation': conversation,
        'tags': tags,
        'comments_count': conversation.approved_comments.count(),
        'votes_count': conversation.votes.count(),
        'favorites_count': favorites.filter(conversation=conversation).count(),
        'user': user,
        'csrf_input': csrf_input(request),
        'show_user_actions': is_authenticated,
        'is_favorite': is_favorite,
        **kwargs,
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
def conversation_ask_create_comment(conversation, request=None, **kwargs):
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
def conversation_ask_opinion_group(conversation, request=None, **kwargs):
    """
    Render comment form for one conversation.
    """
    n_groups = 3
    group_id = 2
    msg = _('This conversation has {n_groups} groups, '
            'and you are in group {group_id}.').format(n_groups=n_groups,
                                                       group_id=group_id)
    return extra_content(_('Opinion groups'), msg, icon='chart-pie')


#
# Comments
#
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
        'comment': comment,
        'rejection_reasons': dict(models.Comment.REJECTION_REASON),
        'csrf_input': csrf_input(request),
        **kwargs,
    }


@with_template(models.Comment, role='list-item')
def comment_list_item(comment, **kwargs):
    """
    Show each comment as an item in a list of comments.
    """

    rejection_reason = comment.rejection_reason
    if rejection_reason in dict(models.Comment.REJECTION_REASON) and comment.status == comment.STATUS.rejected:
        rejection_reason = dict(models.Comment.REJECTION_REASON)[comment.rejection_reason]
    else:
        rejection_reason = None
    return {
        'rejection_reasons': dict(models.Comment.REJECTION_REASON),
        'comment': comment,
        'content': comment.content,
        'creation_date': comment.created.strftime('%d-%m-%Y às %Hh %M'),
        'conversation_url': comment.conversation.get_absolute_url(),
        'status': comment.status,
        'status_name': dict(models.Comment.STATUS)[comment.status].capitalize(),
        'rejection_reason': rejection_reason,

        # Votes
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
