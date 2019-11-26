from sidekick import import_later

from boogie.rest import rest_api
from ej_conversations.models import Conversation
from . import models
from .utils import cluster_shapes

math = import_later(".math", package=__package__)


@rest_api.link(Conversation, name="clusterization")
def clusterization_link(request, conversation):
    try:
        clusterization = conversation.clusterization
    except models.Clusterization.DoesNotExist:
        return None
    else:
        return rest_api.get_hyperlink(clusterization, request)


#
# Cluster info
#
@rest_api.detail_action(models.Clusterization)
def clusters(clusterization):
    return clusterization.clusters.all()


@rest_api.detail_action(models.Clusterization)
def affinities(request, clusterization):
    return cluster_shapes(clusterization, user=request.user)


@rest_api.property(models.Cluster)
def user_list(cluster):
    return list(cluster.users.all().values_list("id", flat=True))


#
# Stereotypes and votes
#
@rest_api.detail_action(models.Clusterization)
def stereotypes(clusterization):
    return clusterization.stereotypes.all()
