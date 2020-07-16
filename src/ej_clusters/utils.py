import contextlib

import sidekick as sk
from django.db import transaction
from django.http import Http404

from ej_clusters.math import compute_cluster_affinities


@contextlib.contextmanager
def use_transaction(which=None, **kwargs):
    """
    Context manager that puts the block inside a transaction of the specified
    kind.
    """
    kinds = {"atomic", "commit", "rollback"}

    if which in kinds:
        kwargs[which] = True
    elif which is not None:
        raise ValueError(f"invalid operation: {which}")

    methods, args = sk.separate(kinds.__contains__, kwargs)
    methods = [getattr(transaction, k) for k in methods if kwargs[k]]
    kwargs = {k: kwargs[k] for k in args}

    if not methods:
        yield None
    else:
        method, *rest = methods
        rest = {k: True for k in rest}
        with use_transaction(**rest, **kwargs), method(**kwargs) as handler:
            yield handler


def check_stereotype(stereotype, user):
    if stereotype.owner != user:
        raise Http404
    return stereotype


def cluster_shapes(clusterization, clusters=None, user=None):
    """
    Return a list of cluster shapes from given clusterization object.

    Args:
        clusterization:
            A clusterization instance
        clusters (queryset):
            Optional sequence of clusters. Use all clusters in clusterization
            if not given.
        user (User):
            Optional user instance. If given, highlight all clusters the user
            belongs to.
    """
    clusters = clusterization.clusters if clusters is None else clusters
    shapes = compute_cluster_affinities(clusters.votes_table("mean"))
    ids = list(shapes.keys())
    names = {c.id: c.name for c in clusters}

    if user is None:
        user_cluster_id = set()
    else:
        user_cluster_id = set(
            clusters.filter(clusterization_id=clusterization.id).values_list("id", flat=True)
        )

    result = {}
    for k, shape in shapes.items():
        old = shape["intersections"]
        shape["intersections"] = [old[id] for id in ids]
        try:
            shape["name"] = names[k]
        except KeyError:
            continue
        if k in user_cluster_id:
            shape["highlight"] = True
        result[k] = shape

    return result
