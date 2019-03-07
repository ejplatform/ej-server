import logging
from random import randrange

from django.db.models import Window, Count, Q
from django.db.models.functions import FirstValue

from boogie.models import QuerySet, F
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

    def cache_annotations(self, *values, user=None, prefix='', **kwargs):
        """
        Annotate each conversation with the progress made by the given user.
        """
        for arg in values:
            kwargs.setdefault(arg, True)

        annotations = {}
        prefix = prefix or ''

        # First tag
        if kwargs.pop('first_tag', False):
            annotations[prefix + 'first_tag'] = Window(FirstValue('tags__name'))

        # Count comments
        if kwargs.pop('n_comments', False):
            annotations[prefix + 'n_comments'] = \
                Count('comments', filter=Q(comments__status=Comment.STATUS.approved), distinct=True)

        # Count favorites
        if kwargs.pop('n_favorites', False):
            annotations[prefix + 'n_favorites'] = \
                Count('favorites')

        # Count votes
        if kwargs.pop('n_votes', False):
            annotations[prefix + 'n_votes'] = Count('comments__votes')

        # Count votes for user
        if kwargs.pop('n_user_votes', False):
            annotations[prefix + 'n_user_votes'] = \
                Count('comments__votes', filter=Q(comments__votes__author=user))

        # Author name
        if kwargs.pop('author_name', False):
            annotations[prefix + 'author_name'] = F('author__name')

        if kwargs:
            raise TypeError(f'bad attribute: {kwargs.popitem()[0]}')

        if not annotations:
            return self
        return self.annotate(**annotations)
