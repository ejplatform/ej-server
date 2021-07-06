from functools import lru_cache

from boogie.router import Router
from django.contrib.auth import get_user_model
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.utils.translation import ugettext as _, ugettext_lazy
from sidekick import import_later

from ej_clusters.models import Cluster
from ej_conversations.models import Conversation
from ej_conversations.routes import conversation_url
from ej_conversations.utils import check_promoted
from .routes import EXPOSED_PROFILE_FIELDS

pd = import_later("pandas")

urlpatterns = Router(
    base_path=conversation_url + "reports/",
    template="ej_dataviz/report/{name}.jinja2",
    models={"conversation": Conversation, "cluster": Cluster},
    login=True,
    perms=["ej.can_view_report:conversation"],
)
app_name = "ej_dataviz"
User = get_user_model()


#
# Base report URLs
#
@urlpatterns.route("")
def index(request, conversation, slug, check=check_promoted):
    check(conversation, request)
    user = request.user
    can_view_detail = user.has_perm("ej.can_view_report_detail", conversation)
    statistics = conversation.statistics()

    # Force clusterization, when possible
    clusterization = getattr(conversation, "clusterization", None)
    if clusterization:
        clusterization.update_clusterization()
        clusters = clusterization.clusters.all()
    else:
        clusters = ()

    return {
        "clusters": clusters,
        "conversation": conversation,
        "statistics": statistics,
        "can_view_detail": can_view_detail,
    }


@urlpatterns.route("users/", perms=["ej.can_view_report_detail"])
def users(request, conversation, slug, check=check_promoted):
    if not request.user.has_perm("ej.can_view_report_detail"):
        raise Http404
    return {"conversation": check(conversation, request)}


# ==============================================================================
# Votes raw data
# ------------------------------------------------------------------------------


@urlpatterns.route("data/votes.<fmt>", perms=["ej.can_view_report_detail"])
def votes_data(request, conversation, fmt, slug, check=check_promoted):
    check(conversation, request)
    filename = conversation.slug + "-votes"
    votes = conversation.votes
    return vote_data_common(votes, filename, fmt)


# FIXME: why is <model:cluster> not working?
# adjust conversation_download_data() after fixing this bug
@urlpatterns.route("data/cluster-<int:cluster_id>/votes.<fmt>", perms=["ej.can_view_report_detail"])
def votes_data_cluster(request, conversation, fmt, cluster_id, slug, check=check_promoted):
    check(conversation, request)
    cluster = get_cluster_or_404(cluster_id, conversation)
    filename = conversation.slug + f"-{slugify(cluster.name)}-votes"
    return vote_data_common(cluster.votes.all(), filename, fmt)


def vote_data_common(votes, filename, fmt):
    """
    Common implementation for votes_data and votes_data_cluster
    """
    df = votes_as_dataframe(votes)
    return data_response(df, fmt, filename)


def votes_as_dataframe(votes):
    columns = (
        "author__email",
        "author__name",
        "author__id",
        "author__metadata__analytics_id",
        "author__metadata__mautic_id",
        "comment__content",
        "comment__id",
        "comment__conversation",
        "choice",
    )
    df = votes.dataframe(*columns)
    df.columns = (
        "email",
        "author",
        "author_id",
        "author__metadata__analytics_id",
        "author__metadata__mautic_id",
        "comment",
        "comment_id",
        "conversation_id",
        "choice",
    )
    votes_timestamps = list(map(lambda x: x[0].timestamp(), list(votes.values_list("created"))))
    df["created"] = votes_timestamps
    df.choice = list(map({-1: "disagree", 1: "agree", 0: "skip"}.get, df["choice"]))
    return df


# ==============================================================================
# Comments raw data
# ------------------------------------------------------------------------------


@urlpatterns.route("data/comments.<fmt>")
def comments_data(request, conversation, fmt, slug, check=check_promoted):
    check(conversation, request)
    filename = conversation.slug + "-comments"
    return comments_data_common(conversation.comments, None, filename, fmt)


@urlpatterns.route("data/cluster-<cluster_id>/comments.<fmt>")
def comments_data_cluster(request, conversation, fmt, cluster_id, slug, check=check_promoted):
    check(conversation, request)
    cluster = get_cluster_or_404(cluster_id, conversation)
    filename = conversation.slug + f"-{slugify(cluster.name)}-comments"
    return comments_data_common(conversation.comments, cluster.votes, filename, fmt)


def comments_data_common(comments, votes, filename, fmt):
    df = comments.statistics_summary_dataframe(votes=votes)
    df = comments.extend_dataframe(df, "id", "author__email", "author__id", "created")
    # Adjust column names
    columns = [
        "content",
        "id",
        "author__email",
        "author__id",
        "agree",
        "disagree",
        "skipped",
        "convergence",
        "participation",
        "created",
    ]
    df = df[columns]
    df.columns = ["comment", "comment_id", "author", "author_id", *columns[4:]]
    return data_response(df, fmt, filename)


# ==============================================================================
# Users raw data
# ------------------------------------------------------------------------------


@urlpatterns.route("data/users.<fmt>")
def users_data(request, conversation, fmt, slug, check=check_promoted):
    check(conversation, request)
    filename = conversation.slug + "-users"
    df = get_user_data(conversation)
    try:
        clusters = conversation.clusterization.clusters.all()
    except AttributeError:
        pass
    else:
        # Retrieve non empty clusters.
        data = clusters.values_list("users__id", "name", "id")
        data = filter(lambda x: x[0], data)
        extra = pd.DataFrame(data, columns=["user", "cluster", "cluster_id"])
        extra.index = extra.pop("user")
        df[["cluster", "cluster_id"]] = extra
        df["cluster_id"] = df.cluster_id.fillna(-1).astype(int)
    return data_response(df, fmt, filename)


def get_user_data(conversation):
    df = conversation.users.statistics_summary_dataframe(extend_fields=("id", *EXPOSED_PROFILE_FIELDS))
    df = df[
        [
            "email",
            "id",
            "name",
            *EXPOSED_PROFILE_FIELDS,
            "agree",
            "disagree",
            "skipped",
            "convergence",
            "participation",
        ]
    ]
    df.columns = ["email", "user_id", *df.columns[2:]]
    return df


# ==============================================================================
# Clusters raw data
# ------------------------------------------------------------------------------


def comments_stats_by_cluster(clusters):
    rows = []

    for cluster in clusters:
        stats = cluster.comments_statistics_summary_dataframe(normalization=100.0)
        for index, row in stats.iterrows():
            data = {}
            data["agree"] = row.agree
            data["disagree"] = row.disagree
            data["skipped"] = row.skipped
            data["cluster_name"] = cluster.name
            data["content"] = row.content
            data["participation"] = row.participation
            rows.append(data)

    return pd.DataFrame(rows)


def clusters_data_common(clusters, filename, fmt):
    df = comments_stats_by_cluster(clusters)
    return data_response(df, fmt, filename)


#
# Auxiliary functions
#


def data_response(data: pd.DataFrame, fmt: str, filename: str, translate=True):
    """
    Prepare data response for file from dataframe.
    """
    response = HttpResponse(content_type=f"text/{fmt}")
    if translate:
        data = data.copy()
        data.columns = [_(x) for x in data.columns]
    response["Content-Disposition"] = f"attachment; filename={filename}.{fmt}"
    if fmt == "json":
        data.to_json(response, orient="records", date_format="iso")
    elif fmt == "csv":
        data.to_csv(response, index=False, mode="a", float_format="%.3f")
    elif fmt == "msgpack":
        data.to_msgpack(response, encoding="utf-8")
    elif fmt == "xlsx":
        data.to_excel(response, filename, index=False)
    else:
        raise ValueError(f"invalid format: {fmt}")
    return response


def get_cluster_or_404(cluster_id, conversation=None):
    """
    Return cluster and checks if cluster belongs to conversation
    """
    cluster = get_object_or_404(Cluster, id=cluster_id)
    if conversation is not None and cluster.clusterization.conversation_id != conversation.id:
        raise Http404
    return cluster


@lru_cache(1)
def get_translation_map():
    _ = ugettext_lazy
    return {
        "agree": _("agree"),
        "author": _("author"),
        "author_id": _("author_id"),
        "choice": _("choice"),
        "cluster": _("cluster"),
        "cluster_id": _("cluster_id"),
        "comment": _("comment"),
        "comment_id": _("comment_id"),
        "convergence": _("convergence"),
        "disagree": _("disagree"),
        "email": _("email"),
        "id": _("id"),
        "name": _("name"),
        "participation": _("participation"),
        "skipped": _("skipped"),
    }
