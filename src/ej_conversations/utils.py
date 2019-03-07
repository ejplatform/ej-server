from logging import getLogger

from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseServerError
from django.utils.translation import ugettext_lazy as _
from hyperpython import a
from sidekick import import_later

log = getLogger('ej')
models = import_later('.models', package=__package__)
forms = import_later('.forms', package=__package__)


#
# Functions
#
def check_promoted(conversation, request):
    """
    Raise a Http404 if conversation is not promoted
    """
    if not conversation.is_promoted:
        raise Http404
    if conversation.is_hidden and not request.user.has_perm('ej.can_edit_conversation', conversation):
        raise Http404
    return conversation


def process_conversation_detail_post(request, conversation, form):
    """
    Process a POST in a conversation:detail view..
    """

    runner = ConversationDetailPostActions(request, conversation, form)
    action = request.POST['action']
    try:
        method = getattr(runner, 'action_' + action)
    except KeyError:
        log.warning(f'user {request.user.id} se nt invalid POST request: {request.POST}')
        return HttpResponseServerError('invalid action')
    else:
        method(request.POST)


def conversation_admin_menu_links(conversation, user):
    """
    Return administrative links to the conversation menu.
    """

    menu_links = []
    if user.has_perm('ej.can_edit_conversation', conversation):
        url = conversation.get_url('conversation:edit')
        menu_links.append(a(_('Edit'), href=url))
    if user.has_perm('ej.can_moderate_conversation', conversation):
        url = conversation.get_url('conversation:moderate')
        menu_links.append(a(_('Moderate'), href=url))
    return menu_links


def votes_counter(comment, choice=None):
    """
    Count the number of votes in comment.
    """
    if choice is not None:
        return comment.votes.filter(choice=choice).count()
    else:
        return comment.votes.count()


def normalize_status(value):
    """
    Convert status string values to safe db representations.
    """
    from ej_conversations.models import Comment

    if value is None:
        return Comment.STATUS.pending
    try:
        return Comment.STATUS_MAP[value.lower()]
    except KeyError:
        raise ValueError(f'invalid status value: {value}')


#
# Auxiliary classes
#
class ConversationDetailPostActions:
    def __init__(self, request, conversation, form):
        self.request = request
        self.conversation = conversation
        self.user = request.user
        self.form = form

    def action_vote(self, data):
        """
        User is voting in the current comment. We still need to choose a random
        comment to display next.
        """
        vote = data['vote']
        comment_id = data['comment_id']
        try:
            models.Comment.objects.get(id=comment_id).vote(self.user, vote)
            log.info(f'user {self.user.id} voted {vote} on comment {comment_id}')
        except ValidationError:
            # User voted twice and too quickly... We simply ignore the last vote
            log.info(f'duplicated vote for user {self.user.id} on comment {comment_id}')

    def action_comment(self, data):
        """
        User is posting a new comment. We need to validate the form and try to
        keep the same comment that was displayed before.
        """
        if self.form.is_valid():
            new_comment = self.form.cleaned_data['content']
            new_comment = self.conversation.create_comment(self.user, new_comment)
            log.info(f'user {self.user.id} posted comment {new_comment.id} on {self.conversation.id}')

    def action_favorite(self, data):
        """
        User toggled the favorite status of conversation.
        """
        self.conversation.toggle_favorite(self.user)
        log.info(f'user {self.user.id} toggled favorite status of conversation {self.conversation.id}')
