import logging

from boogie.models import F, Value, IntegerField, FieldDoesNotExist
from boogie.models.wordcloud import WordCloudQuerySet
from django.contrib.auth import get_user_model
from django.db.models import Window, Count, Q
from django.db.models.functions import FirstValue

from .comment import Comment
from ..mixins import ConversationMixin

log = logging.getLogger("ej")


class ConversationQuerySet(ConversationMixin, WordCloudQuerySet):
    """
    A table of conversations.
    """

    conversations = lambda self: self

    def authors(self):
        """
        Return all authors from the current conversations.
        """
        return get_user_model().objects.filter(Q(conversations__in=self))

    def promoted(self):
        """
        Show only promoted conversations.
        """
        return self.filter(is_promoted=True)

    def cache_annotations(self, *values, user=None, prefix="", **kwargs):
        """
        Annotate each conversation with the progress made by the given user.
        """
        for arg in values:
            kwargs.setdefault(arg, True)

        annotations = {}
        prefix = prefix or ""

        # First tag
        if kwargs.pop("first_tag", False):
            annotations[prefix + "first_tag"] = Window(FirstValue("tags__name"))

        # Count comments
        if kwargs.pop("n_comments", False):
            annotations[prefix + "n_comments"] = Count(
                "comments",
                filter=Q(comments__status=Comment.STATUS.approved),
                distinct=True,
            )

        # Count favorites
        if kwargs.pop("n_favorites", False):
            annotations[prefix + "n_favorites"] = Count("favorites")

        # Count votes
        if kwargs.pop("n_votes", False):
            annotations[prefix + "n_votes"] = Count("comments__votes")

        # Count votes for user
        if kwargs.pop("n_user_votes", False):
            if user.is_authenticated:
                data = Count("comments__votes", filter=Q(comments__votes__author=user))
            else:
                data = Value(0, IntegerField())
            annotations[prefix + "n_user_votes"] = data

        # Author name
        if kwargs.pop("author_name", False):
            annotations[prefix + "author_name"] = F(AUTHOR_NAME_FIELD)

        if kwargs:
            raise TypeError(f"bad attribute: {kwargs.popitem()[0]}")

        if not annotations:
            return self
        return self.annotate(**annotations)


#
# Constants and configurations
#
try:
    get_user_model()._meta.get_field("name")
    AUTHOR_NAME_FIELD = "author__name"
except FieldDoesNotExist:
    AUTHOR_NAME_FIELD = "author__username"
