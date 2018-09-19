from logging import getLogger
from django.http import HttpResponseServerError, Http404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from hyperpython import a

from boogie import rules
from . import urlpatterns, conversation_url
from ..models import Conversation, Comment

log = getLogger('ej')


@urlpatterns.route('', name='list')
def conversation_list(request):
    return {
        'conversations': Conversation.objects.filter(is_promoted=True),
        'can_add_conversation': request.user.has_perm('ej.can_add_promoted_conversation'),
        'create_url': reverse('conversation:create'),
        'topic': _('A space for adolescents to discuss actions that promote, guarantee and defend their rights'),
        'title': _('Public conversations'),
        'subtitle': _('Participate of conversations and give your opinion with comments and votes!'),
    }


@urlpatterns.route(conversation_url)
def detail(request, conversation):
    if not conversation.is_promoted:
        raise Http404
    return conversation_detail_context(request, conversation)


#
# Auxiliary and re-usable functions
#
def conversation_detail_context(request, conversation):
    """
    Common implementation used by both /conversations/<slug> and inside boards
    in /<board>/conversations/<slug>/
    """
    user = request.user
    is_favorite = user.is_authenticated and conversation.followers.filter(user=user).exists()
    n_comments = rules.compute('ej.remaining_comments', conversation, user)
    comment = None

    # User is voting in the current comment. We still need to choose a random
    # comment to display next.
    if request.POST.get('action') == 'vote':
        vote = request.POST['vote']
        comment_id = request.POST['comment_id']
        Comment.objects.get(id=comment_id).vote(user, vote)
        log.info(f'user {user.id} voted {vote} on comment {comment_id}')

    # User is posting a new comment. We need to validate the form and try to
    # keep the same comment that was displayed before.
    elif request.POST.get('action') == 'comment':
        # FIXME: do not hardcode this and use a proper form!
        new_comment = request.POST['comment'].strip()
        new_comment = new_comment[:210]
        new_comment = conversation.create_comment(user, new_comment)
        log.info(f'user {user.id} posted comment {new_comment.id} on {conversation.id}')

    # User toggled the favorite status of conversation.
    elif request.POST.get('action') == 'favorite':
        conversation.toggle_favorite(user)
        log.info(f'user {user.id} toggled favorite status of conversation {conversation.id}')

    # User is probably trying to something nasty ;)
    elif request.method == 'POST':
        log.warning(f'user {user.id} sent invalid POST request: {request.POST}')
        return HttpResponseServerError('invalid action')
    return {
        # Objects
        'conversation': conversation,
        'comment': comment or conversation.next_comment(user, None),
        'comments_left': n_comments,
        'login_link': login_link(_('login'), conversation),

        # Permissions and predicates
        'is_favorite': is_favorite,
        'can_view_comment': user.is_authenticated,
        'can_comment': user.has_perm('ej.can_comment', conversation),
        'can_edit': user.has_perm('ej.can_edit_conversation', conversation),
        'cannot_comment_reason': '',
    }


def login_link(content, obj):
    path = obj.get_absolute_url()
    return a(content, href=reverse('auth:login') + f'?next={path}')
