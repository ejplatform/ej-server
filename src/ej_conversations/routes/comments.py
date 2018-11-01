from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from boogie import rules
from . import urlpatterns, conversation_url


@urlpatterns.route(conversation_url + 'comments/')
def comment_list(request, conversation, comment):
    if not conversation.is_promoted:
        raise Http404

    user = request.user
    comments = conversation.comments.filter(author=user)
    n_comments = rules.compute('ej_conversations.remaining_comments', conversation, user)
    # rejection_reason = comment.rejection_reason
    # if rejection_reason in dict(Comment.REJECTION_REASON) and comment.status == comment.STATUS.rejected:
    #     rejection_reason = dict(Comment.REJECTION_REASON)[comment.rejection_reason]
    # else:
    #     rejection_reason = None
    return {
        'content_title': _('List conversations'),
        'conversation': conversation,
        'approved': comments.approved(),
        'rejected': comments.rejected(),
        'pending': comments.pending(),
        'remaining_comments': n_comments,
        'can_comment': user.has_perm('ej.can_comment', conversation),
        'can_edit': user.has_perm('ej.can_edit_conversation', conversation),
        'status': comment.status,
        'status_name': dict(models.Comment.STATUS)[comment.status].capitalize(),
        'rejection_reason': rejection_reason,
    }


@urlpatterns.route(conversation_url + 'comments/<model:comment>/', lookup_field={'comment': 'pk'})
def comment_detail(conversation, comment):
    if not conversation.is_promoted:
        raise Http404

    return {
        'conversation': conversation,
        'comment': comment,
    }
