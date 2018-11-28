from logging import getLogger

from django.db import transaction
from django.http import Http404, HttpResponseServerError
from django.shortcuts import redirect

from . import urlpatterns, conversation_url
from .. import forms, models

log = getLogger('ej')


@urlpatterns.route('add/', login=True)
def create(request):
    # TODO: Fix this case of permission in django-boogie
    if not request.user.has_perm('ej.can_add_promoted_conversation'):
        raise Http404

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
    return get_conversation_edit_context(request, conversation)


def get_conversation_edit_context(request, conversation):
    if request.method == 'POST':
        form = forms.ConversationForm(
            data=request.POST,
            instance=conversation,
        )
        if form.is_valid():
            form.instance.save()
            return redirect(conversation.get_absolute_url() + 'moderate/')
    else:
        form = forms.ConversationForm(instance=conversation)

    return {
        'form': form,
        'conversation': conversation,
        'can_promote_conversation': request.user.has_perm('can_publish_promoted'),
        'comments': list(conversation.comments.filter(status='pending')),
        'manage_stereotypes_url': conversation.get_absolute_url() + 'stereotypes/',
    }


@urlpatterns.route(conversation_url + 'moderate/', perms=['ej.can_moderate_conversation'])
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
        'edit_url': conversation.get_absolute_url() + 'edit/',
        'comments': list(conversation.comments.filter(status=status)),
        'tags': tags,
    }
