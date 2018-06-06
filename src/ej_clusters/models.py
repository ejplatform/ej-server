import logging

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from boogie.fields import EnumField
from boogie.rest import rest_api
from ej_conversations.managers import BoogieManager
from ej_conversations.models import Choice
from ej_conversations.models.vote import normalize_choice
from .manager import ClusterManager

log = logging.getLogger('ej')


@rest_api(exclude=['users', 'stereotypes'])
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
        through='UserClusterMap',
    )
    stereotypes = models.ManyToManyField(
        'Stereotype',
        through='StereotypeClusterMap',
    )

    objects = ClusterManager()

    def __str__(self):
        msg = _('{name} ("{conversation}" conversation)')
        return msg.format(name=self.name, conversation=str(self.conversation))


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

    def vote(self, comment, choice, commit=True):
        """
        Cast a single vote for the stereotype.
        """
        choice = normalize_choice(choice)
        log.debug(f'Vote: {self.name} (stereotype) - {choice}')
        vote = StereotypeVote(author=self, comment=comment, choice=choice)
        vote.full_clean()
        if commit:
            vote.save()
        return vote

    def cast_votes(self, choices):
        """
        Create votes from dictionary of comments to choices.
        """
        votes = []
        for comment, choice in choices.items():
            votes.append(self.vote(comment, choice, commit=True))
        StereotypeVote.objects.bulk_update(votes)
        return votes


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
    objects = BoogieManager()

    def __str__(self):
        return f'StereotypeVote({self.stereotype}, value={self.value})'


class UserClusterMap(models.Model):
    """
    A user/cluster M2M that prevents repeated cluster attributions
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    conversation = models.ForeignKey('ej_conversations.Conversation',
                                     on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.conversation_id is None:
            self.conversation_id = self.cluster.conversation_id

    class Meta:
        unique_together = [('user', 'conversation')]


class StereotypeClusterMap(models.Model):
    """
    A user/cluster M2M that prevents repeated cluster attributions
    """
    stereotype = models.ForeignKey(Stereotype, on_delete=models.CASCADE)
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    conversation = models.ForeignKey(
        'ej_conversations.Conversation',
        on_delete=models.CASCADE,
        editable=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.conversation_id is None and self.cluster_id is not None:
            self.conversation_id = self.cluster.conversation_id

    class Meta:
        unique_together = [('stereotype', 'conversation')]


