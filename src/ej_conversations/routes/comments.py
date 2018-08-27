from django.utils.translation import ugettext_lazy as _

from boogie import rules
from . import urlpatterns, conversation_url


@urlpatterns.route(conversation_url + 'comments/')
def comment_list(request, conversation):
    user = request.user
    comments = conversation.comments.filter(author=user)
    n_comments = rules.compute('ej_conversations.remaining_comments', conversation, user)
    return {
        'content_title': _('List conversations'),
        'conversation': conversation,
        'approved': comments.approved(),
        'rejected': comments.rejected(),
        'pending': comments.pending(),
        'remaining_comments': n_comments,
        'can_comment': user.has_perm('ej.can_comment', conversation),
        'can_edit': user.has_perm('ej.can_edit_conversation', conversation),
    }


@urlpatterns.route(conversation_url + 'comments/<model:comment>/', lookup_field={'comment': 'pk'})
def comment_detail(conversation, comment):
    return {
        'conversation': conversation,
        'comment': comment,
    }
