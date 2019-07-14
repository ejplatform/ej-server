from logging import getLogger

from boogie import models, rules
from boogie.fields import EnumField
from boogie.rest import rest_api
from model_utils.models import TimeStampedModel
from sidekick import delegate_to, lazy, placeholder as this

from .querysets import ClusterizationManager
from .stereotype import Stereotype
from .stereotype_vote import StereotypeVote
from ..enums import ClusterStatus
from ..utils import use_transaction

NOT_GIVEN = object()
log = getLogger("ej")


@rest_api(["conversation", "cluster_status"])
class Clusterization(TimeStampedModel):
    """
    Manages clusterization tasks for a given conversation.
    """

    conversation = models.OneToOneField(
        "ej_conversations.Conversation", on_delete=models.CASCADE, related_name="clusterization"
    )
    cluster_status = EnumField(ClusterStatus, default=ClusterStatus.PENDING_DATA)
    pending_comments = models.ManyToManyField(
        "ej_conversations.Comment", related_name="pending_in_clusterizations", editable=False, blank=True
    )
    pending_votes = models.ManyToManyField(
        "ej_conversations.Vote", related_name="pending_in_clusterizations", editable=False, blank=True
    )

    unprocessed_comments = property(lambda self: self.pending_comments.count())
    unprocessed_votes = property(lambda self: self.pending_votes.count())
    comments = delegate_to("conversation")
    users = delegate_to("conversation")
    votes = delegate_to("conversation")
    owner = delegate_to("conversation", name="author")

    @property
    def stereotypes(self):
        return Stereotype.objects.filter(clusters__in=self.clusters.all())

    @property
    def stereotype_votes(self):
        return StereotypeVote.objects.filter(comment__in=self.comments.all())

    #
    # Statistics and annotated values
    #
    n_clusters = lazy(this.clusters.count())
    n_stereotypes = lazy(this.stereotypes.count())
    n_stereotype_votes = lazy(this.stereotype_votes.count())

    objects = ClusterizationManager()

    class Meta:
        ordering = ["conversation_id"]

    def __str__(self):
        clusters = self.clusters.count()
        return f"{self.conversation} ({clusters} clusters)"

    def get_absolute_url(self):
        return self.conversation.url("cluster:index")

    def update_clusterization(self, force=False, atomic=False):
        """
        Update clusters if necessary, unless force=True, in which it
        unconditionally updates the clusterization.
        """
        if force or rules.test_rule("ej.must_update_clusterization", self):
            log.info(f"[clusters] updating cluster: {self.conversation}")

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
