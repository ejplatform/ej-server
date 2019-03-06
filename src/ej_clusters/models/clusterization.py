from logging import getLogger

from django.urls import reverse
from model_utils.models import TimeStampedModel
from sidekick import delegate_to, lazy

from boogie import models, rules
from boogie.fields import EnumField
from boogie.rest import rest_api
from ej_conversations.models import Conversation
from .querysets import ClusterizationManager
from .stereotype import Stereotype
from ..enums import ClusterStatus
from ..utils import use_transaction

NOT_GIVEN = object()
log = getLogger('ej')


@rest_api(['conversation', 'cluster_status'])
class Clusterization(TimeStampedModel):
    """
    Manages clusterization tasks for a given conversation.
    """
    conversation = models.OneToOneField(
        'ej_conversations.Conversation',
        on_delete=models.CASCADE,
        related_name='clusterizations',
    )
    cluster_status = EnumField(
        ClusterStatus,
        default=ClusterStatus.PENDING_DATA,
    )
    pending_comments = models.ManyToManyField(
        'ej_conversations.Comment',
        related_name='pending_in_clusterizations',
        editable=False,
        blank=True,
    )
    pending_votes = models.ManyToManyField(
        'ej_conversations.Vote',
        related_name='pending_in_clusterizations',
        editable=False,
        blank=True,
    )

    unprocessed_comments = property(lambda self: self.pending_comments.count())
    unprocessed_votes = property(lambda self: self.pending_votes.count())
    comments = delegate_to('conversation')
    users = delegate_to('conversation')
    votes = delegate_to('conversation')
    owner = delegate_to('conversation', name='author')

    @property
    def stereotypes(self):
        return Stereotype.objects.filter(clusters__in=self.clusters.all())

    objects = ClusterizationManager()

    class Meta:
        ordering = ['conversation_id']

    def __str__(self):
        clusters = self.clusters.count()
        return f'{self.conversation} ({clusters} clusters)'

    def get_absolute_url(self):
        args = {'conversation': self.conversation}
        return reverse('cluster:index', kwargs=args)

    def update_clusterization(self, force=False, atomic=True):
        """
        Update clusters if necessary, unless force=True, in which it
        unconditionally updates the clusterization.
        """
        if force or rules.test_rule('ej.must_update_clusterization', self):
            log.info(f'[clusters] updating cluster: {self.conversation}')

            if self.clusters.count() == 0:
                if self.cluster_status == ClusterStatus.ACTIVE:
                    self.cluster_status = ClusterStatus.PENDING_DATA
                self.save()
                return

            with use_transaction(atomic=atomic):
                try:
                    self.clusters.clusterize_from_votes()
                except ValueError:
                    return
                self.pending_comments.all().delete()
                self.pending_votes.all().delete()
                if self.cluster_status == ClusterStatus.PENDING_DATA:
                    self.cluster_status = ClusterStatus.ACTIVE
                self.save()


#
# AUXILIARY METHODS
#
def get_clusterization(conversation, default=NOT_GIVEN):
    """
    Initialize a clusterization object for the given conversation, if it does
    not exist.
    """
    try:
        return conversation.clusterization
    except Clusterization.DoesNotExist:
        if default is NOT_GIVEN:
            mgm, _ = Clusterization.objects.get_or_create(conversation=conversation)
            return mgm
        else:
            return default


Conversation.get_clusterization = get_clusterization
Conversation._clusterization = lazy(get_clusterization)
Conversation.clusters = delegate_to('_clusterization')
