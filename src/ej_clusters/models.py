from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from boogie.fields import EnumField
from ej_conversations.models import Choice


class Cluster(TimeStampedModel):
    """
    Represents an opinion group.
    """
    conversation = models.ForeignKey(
        'ej_conversations.Conversation',
        on_delete=models.CASCADE,
        related_name='clusters',
    )
    name = models.CharField(
        _('Name'),
        max_length=64,
        blank=True,
    )
    users = models.ManyToManyField(
        get_user_model(),
    )
    stereotypes = models.ManyToManyField(
        'Stereotype',
    )

    __str__ = (lambda self: self.name)


class Stereotype(models.Model):
    """
    A "fake" user created to help with classification.
    """
    name = models.CharField(
        _('Name'),
        max_length=64,
        unique=True,
    )
    description = models.TextField(
        _('Description'),
        blank=True,
    )

    __str__ = (lambda self: self.name)


class StereotypeVote(models.Model):
    """
    Similar to vote, but it is not associated with a comment.

    It forms a m2m relationship between Stereotypes and comments.
    """
    author = models.ForeignKey(
        'Stereotype',
        related_name='votes',
        on_delete=models.CASCADE,
    )
    comment = models.ForeignKey(
        'ej_conversations.Comment',
        related_name='stereotype_votes',
        on_delete=models.CASCADE,
    )
    choice = EnumField(Choice)

    def __str__(self):
        return f'StereotypeVote({self.stereotype}, value={self.value})'
