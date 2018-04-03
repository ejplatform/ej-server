from django.db import models
from django.utils.translation import ugettext_lazy as _

from ej.conversations.models.comment import Comment
from ej.conversations.models.conversation import Conversation
from ej.conversations.models.vote import Vote


class Stereotype(models.Model):
    """
    A "fake" user created to help with classification.
    """
    name = models.CharField(
        _('Name'),
        max_length=140,
        unique=True,
    )
    description = models.TextField(
        _('Description'),
        blank=True,
    )
    conversations = models.ManyToManyField(
        Conversation,
        related_name='conversations',
    )


class StereotypeVote(models.Model):
    """
    Similar to vote, but it is not associated with a comment.

    It forms a m2m relationship between Stereotypes and comments.
    """
    stereotype = models.ForeignKey(
        Stereotype,
        related_name='stereotype_votes',
        on_delete=models.CASCADE,
    )
    comment = models.ForeignKey(
        Comment,
        related_name='stereotype_votes',
        on_delete=models.CASCADE,
    )
    value = models.IntegerField(
        _('Value'),
        choices=Vote.VOTE_CHOICES,
    )
