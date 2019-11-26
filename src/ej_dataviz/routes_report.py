from boogie.router import Router
from django.contrib.auth import get_user_model
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
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
    columns = "author__email", "author__name", "author__id", "comment__content", "comment__id", "choice"
    df = votes.dataframe(*columns)
    df.columns = "email", "author", "author_id", "comment", "comment_id", "choice"
    df.choice = list(map({-1: "disagree", 1: "agree", 0: "skip"}.get, df["choice"]))
    return data_response(df, fmt, filename)


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
    df = comments.extend_dataframe(df, "id", "author__email", "author__id")

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


#
# Auxiliary functions
#
def data_response(data: pd.DataFrame, fmt: str, filename: str):
    """
    Prepare data response for file from dataframe.
    """
    response = HttpResponse(content_type=f"text/{fmt}")
    response["Content-Disposition"] = f"attachment; filename={filename}.{fmt}"
    if fmt == "json":
        data.to_json(response, orient="records")
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
