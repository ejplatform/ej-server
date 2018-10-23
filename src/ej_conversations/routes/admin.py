from django.db import transaction
from django.http import Http404, HttpResponseServerError
from django.shortcuts import redirect
from logging import getLogger

from ej_boards.models import BoardSubscription
from . import urlpatterns, conversation_url
from .. import forms, models

log = getLogger('ej')


@urlpatterns.route('add/', login=True, perms=['ej.can_add_promoted_conversation'])
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
                   perms=['ej.can_edit_conversation'])
def edit(request, conversation):
    if not conversation.is_promoted:
        raise Http404
    return edit_context(request, conversation)


@urlpatterns.route(conversation_url + 'moderate/', perms=['ej.can_moderate_conversation'])
def moderate(request, conversation):
    if not conversation.is_promoted:
        raise Http404

    return moderate_context(request, conversation)


def edit_context(request, conversation):
    comments = []
    board = None
    if request.method == 'POST':
        form = forms.ConversationForm(
            data=request.POST,
            instance=conversation,
        )
        if form.is_valid():
            form.instance.save()
            return redirect(conversation.get_absolute_url() + 'moderate/')
    else:
        boards = BoardSubscription.objects.filter(conversation=conversation)
        if boards.count() > 0:
            board = boards[0].board
        form = forms.ConversationForm(instance=conversation)
        for comment in models.Comment.objects.filter(conversation=conversation, status='pending'):
            comments.append(comment)

    user = request.user
    return {
        'conversation': conversation,
        'can_promote_conversation': user.has_perm('can_publish_promoted'),
        'comments': comments,
        'board': board,
        'form': form,
        'manage_stereotypes_url': conversation.get_absolute_url() + 'stereotypes/',
    }


def moderate_context(request, conversation):
    comments = []
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
    status = request.GET.get('status')
    status = 'pending' if status not in ['pending', 'approved', 'rejected'] else status
    for comment in models.Comment.objects.filter(conversation=conversation, status=status):
        comments.append(comment)
    return {
        'conversation': conversation,
        'comment_status': status,
        'edit_url': conversation.get_absolute_url() + 'edit/',
        'comments': comments,
    }
