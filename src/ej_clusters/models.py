import logging

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from boogie import rules
from boogie.fields import EnumField
from boogie.rest import rest_api
from ej_conversations.managers import BoogieManager
from ej_conversations.models import Choice
from ej_conversations.models.vote import normalize_choice
from sidekick import delegate_to
from .manager import ClusterManager
from .types import ClusterStatus

log = logging.getLogger('ej')


@rest_api()
class Clusterization(TimeStampedModel):
    """
    Manages clusterization tasks for a given conversation.
    """
    conversation = models.OneToOneField(
        'ej_conversations.Conversation',
        on_delete=models.CASCADE,
        related_name='clusterization',
    )
    cluster_status = EnumField(
        ClusterStatus,
        default=ClusterStatus.PENDING_DATA,
    )
    unprocessed_votes = models.PositiveSmallIntegerField(
        default=0,
        editable=False,
    )
    unprocessed_comments = models.PositiveSmallIntegerField(
        default=0,
        editable=False,
    )

    def __str__(self):
        clusters = self.clusters.count()
        return f'{self.conversation} ({clusters} clusters)'

    def get_absolute_url(self):
        args = {'conversation': self.conversation}
        return reverse('cluster:index', kwargs=args)

    def force_update(self, commit=True):
        """
        Force a cluster update.

        Used internally by .update() when an update is necessary.
        """
        log.info(f'[clusters] updating cluster: {self.conversation}')

        self.unprocessed_comments = 0
        self.unprocessed_votes = 0
        if commit:
            self.save()

    def update(self, commit=True):
        """
        Update clusters if necessary.
        """
        if self.requires_update():
            self.force_update(commit=False)
            if self.cluster_status == ClusterStatus.PENDING_DATA:
                self.cluster_status = ClusterStatus.ACTIVE
            if commit:
                self.save()

    def requires_update(self):
        """
        Check if update should be recomputed.
        """
        conversation = self.conversation
        if self.cluster_status == ClusterStatus.PENDING_DATA:
            rule = rules.get_rule('ej_clusters.conversation_has_sufficient_data')
            if not rule.test(conversation):
                log.info(f'[clusters] {conversation}: not enough data to start clusterization')
                return False
        elif self.cluster_status == ClusterStatus.DISABLED:
            return False

        rule = rules.get_rule('ej_clusters.must_update_clusters')
        return rule.test(conversation)


@rest_api(exclude=['users', 'stereotypes'])
class Cluster(TimeStampedModel):
    """
    Represents an opinion group.
    """

    clusterization = models.ForeignKey(
        'Clusterization',
        on_delete=models.CASCADE,
        related_name='clusters',
    )
    name = models.CharField(
        _('Name'),
        max_length=64,
    )
    users = models.ManyToManyField(
        get_user_model(),
        related_name='clusters',
        blank=True,
    )
    stereotypes = models.ManyToManyField(
        'Stereotype',
        related_name='clusters',
    )

    conversation = delegate_to('clusterization')
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


#
# Auxiliary methods
#
def get_clusterization(conversation):
    try:
        return conversation.clusterization
    except Clusterization.DoesNotExist:
        mgm, _ = Clusterization.objects.get_or_create(conversation=conversation)
        return mgm
