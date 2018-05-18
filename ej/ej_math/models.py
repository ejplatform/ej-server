from django.db import models
from django.contrib.auth import get_user_model
from boogie.fields import EnumField, Enum
from django.utils.translation import ugettext_lazy as _
from picklefield import PickledObjectField

NumpyArrayField = PickledObjectField


def UserRef(**kwargs):
    kwargs.setdefault('on_delete', models.CASCADE)
    return models.ForeignKey(get_user_model(), **kwargs)


def ConversationRef(**kwargs):
    kwargs.setdefault('on_delete', models.CASCADE)
    return models.ForeignKey('ej_conversations.Conversation', **kwargs)


def CommentRef(**kwargs):
    kwargs.setdefault('on_delete', models.CASCADE)
    return models.ForeignKey('ej_conversations.Comment', **kwargs)


class ClusterType(Enum):
    """
    Cluster type.
    """

    ADHOC_CLUSTER = 0, _('Adhoc cluster')
    OPINION_GROUP = 1, _('Opinion group')


class ConversationCluster(models.Model):
    """
    Represents an arbitrary grouping of users associated with a conversation.
    """

    conversation = ConversationRef()
    stereotype = models.ForeignKey(
        'ej_conversations.Stereotype',
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    kind = EnumField(ClusterType)
    index = models.IntegerField(default=0)
    users = models.ManyToManyField(get_user_model())

    class Meta:
        unique_together = [('conversation', 'index', 'kind')]
        ordering = 'index'


class CommentQueue(models.Model):
    """
    Represents a pre-computed priority queue for non-voted comments.
    """

    conversation = ConversationRef()
    user = UserRef()
    comments = models.CommaSeparatedIntegerField(null=True, blank=True)

    class Meta:
        unique_together = [('conversation', 'user')]


class CommentData(models.Model):
    """
    Keeps track of statistics about a comment and cache this info on the
    database.
    """
    comment = CommentRef(unique=True)
    number_of_votes = models.PositiveSmallIntegerField()
    missing_votes = models.PositiveSmallIntegerField()
    vote_distribution = NumpyArrayField()
    cluster_vote_distribution = NumpyArrayField()


class UserParticipationStatistics(models.Model):
    """
    Db-stored statistics for user participation on a conversation.
    """
    conversation = ConversationRef()
    user = UserRef()
    cluster = models.ForeignKey(ConversationCluster, on_delete=models.CASCADE)
    number_of_votes = models.PositiveSmallIntegerField()
    missing_votes = models.PositiveSmallIntegerField()
    vote_distribution = NumpyArrayField()

    class Meta:
        unique_together = [('conversation', 'user')]


