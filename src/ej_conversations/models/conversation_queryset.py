import logging
from random import randrange

from django.db.models import Window, Count, Q
from django.db.models.functions import FirstValue

from boogie.models import QuerySet
from .comment import Comment
from ..mixins import ConversationMixin

log = logging.getLogger('ej')


class ConversationQuerySet(ConversationMixin, QuerySet):
    """
    A table of conversations.
    """
    conversations = (lambda self: self)

    def random(self, user=None):
        """
        Return a random conversation.

        If user is given, tries to select the conversation that is most likely
        to engage the given user.
        """
        size = self.count()
        return self.all()[randrange(size)]

    def promoted(self):
        """
        Show only promoted conversations.
        """
        return self.filter(is_promoted=True)

    def annotate_with(self, *values, user=None, **kwargs):
        """
        Annotate each conversation with the progress made by the given user.

        Args:
            tag_first:
                Annotate with the first tag in the list of tags.
            approved_comments:
                Annotate with the number of approved comments.
            user_votes:
                Annotate with the number of votes cast by user.
        """
        for arg in values:
            kwargs.setdefault(arg, True)

        annotations = {}
        if kwargs.pop('tag_first', False):
            annotations['annotation_tag_first'] = \
                Window(FirstValue('tags__name'))
        if kwargs.pop('approved_comments', False):
            annotations['annotation_approved_comments'] = \
                Count('comments', filter=Q(comments__status=Comment.STATUS.approved), distinct=True)
        if kwargs.pop('user_votes', False):
            annotations['annotation_user_votes'] = \
                Count('comments__votes', filter=Q(comments__votes__author=user))

        if kwargs:
            raise TypeError(f'bad attribute: {kwargs.popitem()[0]}')

        if not annotations:
            return self
        return self.annotate(**annotations)
