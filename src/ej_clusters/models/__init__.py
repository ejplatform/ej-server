from django.utils.translation import ugettext as _
from hyperpython import a as _a

from ej.components import register_menu
from .cluster import Cluster
from .cluster_queryset import ClusterQuerySet, ClusterManager
from .clusterization import Clusterization
from .querysets import ClusterizationQuerySet, ClusterizationManager, StereotypeVoteQuerySet, \
    StereotypeQuerySet
from .stereotype import Stereotype
from .stereotype_vote import StereotypeVote


@register_menu('conversations:detail-admin')
def __(request, conversation):
    return [
        _a(_('Edit groups'), href=conversation.url('cluster:edit')),
        _a(_('Manage personas'), href=conversation.url('cluster:stereotype-votes')),
    ]


@register_menu('conversations:detail-actions')
def __(request, conversation):
    return [
        _a(_('Opinion groups'), href=conversation.url('cluster:index')),
    ]
