from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from model_utils.models import TimeStampedModel
from sidekick import lazy

from ..fields import ConversationRef, UserRef


# TODO: this model is not used yet
class CommentQueue(TimeStampedModel):
    """
    Represents a pre-computed priority queue for non-voted comments.
    """

    conversation = ConversationRef()
    user = UserRef()
    comments = models.TextField(
        blank=True,
        validators=[validate_comma_separated_integer_list],
    )
    comments_list = lazy(lambda self: list(map(int, self.comments)))

    class Meta:
        unique_together = [('conversation', 'user')]
