from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from boogie import rules

from . import urlpatterns, conversation_url
from .. import forms, models


@urlpatterns.route('add/', perms=['ej_conversations.can_add_conversation'])
def create(request, owner=None):
    # Cannot create pages for other users
    if owner and owner != request.user:
        raise Http404

    if rules.test_rule('ej_conversations.has_conversation', request.user):
        Form = forms.ConversationForm
    else:
        Form = forms.FirstConversationForm

    if request.method == 'POST':
        form = Form(request.POST)
        if form.is_valid():
            try:
                models.ConversationBoard.objects.create(
                    name=form.cleaned_data['board_name'],
                    owner=request.user
                )
            except KeyError:
                pass

            conversation = form.save(commit=False)
            conversation.author = request.user
            conversation.save()

            for tag in form.cleaned_data['tags']:
                conversation.tags.add(tag)
            return redirect(conversation.get_absolute_url())
    else:
        form = Form()

    return {
        'content_title': _('Create conversation'),
        'form': form,
    }


@urlpatterns.route(conversation_url + 'edit/',
                   perms=['ej_conversations.can_edit_conversation'])
def edit(request, conversation, owner=None):
    if request.method == 'POST':
        form = forms.ConversationForm(
            data=request.POST,
            instance=conversation,
        )
        if form.is_valid():
            form.instance.save()
            return redirect(conversation.get_absolute_url())
    else:
        form = forms.ConversationForm(instance=conversation)

    return {
        'content_title': _('Edit conversation: {conversation}').format(conversation=conversation),
        'form': form,
    }


@urlpatterns.route(conversation_url + 'moderate/')
def moderate(request, conversation):
    if not request.user.has_perm('ej_conversations.can_moderate_conversation', conversation):
        raise Http404

    comments = []
    if request.method == 'POST':
        comment = models.Comment.objects.get(id=request.POST['comment'])
        comment.status = comment.STATUS.approved if request.POST['vote'] == 'approve' else comment.STATUS.rejected
        comment.rejection_reason = request.POST['rejection_reason']
        comment.save()

    for comment in models.Comment.objects.filter(conversation=conversation, status='pending'):
        if comment.is_pending:
            comments.append(comment)
    return {
        'conversation': conversation,
        'comments': comments,
    }
