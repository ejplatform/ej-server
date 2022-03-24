from functools import lru_cache
import datetime

from boogie.router import Router
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.text import slugify
from django.utils.translation import ugettext as _, ugettext_lazy
from ej_clusters.models.clusterization import Clusterization
from ej_tools.utils import get_host_with_schema
from sidekick import import_later
from django.core.paginator import Paginator

from ej_clusters.models import Cluster
from ej_conversations.models import Conversation
from ej_conversations.utils import check_promoted
from .routes import words
from .models import ToolsLinksHelper
from .utils import OrderByOptions
from .utils import (
    add_id_column,
    filter_comments_by_group,
    get_page,
    get_cluster_names,
    get_comments_dataframe,
    sort_comments_df,
    search_comments_df,
    get_cluster_main_comments,
    get_clusters,
    get_cluster_or_404,
    data_response,
    get_user_data,
    comments_data_common,
    vote_data_common,
)


pd = import_later("pandas")

urlpatterns = Router(
    base_path=f"<model:conversation>/<slug:slug>/" + "reports/",
    template="ej_dataviz/report/{name}.jinja2",
    models={"conversation": Conversation, "cluster": Cluster},
    login=True,
    perms=["ej.can_view_report:conversation"],
)
app_name = "ej_dataviz"
User = get_user_model()


@urlpatterns.route("general-report/")
def general_report(request, conversation, **kwargs):
    check_promoted(conversation, request)
    can_view_detail = request.user.has_perm("ej.can_view_report_detail", conversation)
    statistics = conversation.statistics()

    conversation_clusterization = Clusterization.objects.filter(conversation=conversation)
    conversation_has_stereotypes = False

    if conversation_clusterization.exists():
        conversation_has_stereotypes = conversation_clusterization.stereotypes().count() > 0

    host = get_host_with_schema(request)
    return {
        "conversation": conversation,
        "type_data": "votes-data",
        "can_view_detail": can_view_detail,
        "statistics": statistics,
        "conversation_has_stereotypes": conversation_has_stereotypes,
        "bot": ToolsLinksHelper.get_bot_link(host),
    }


@urlpatterns.route("general-report/words.json")
def report_card_words(request, conversation, **kwargs):
    return words(request, conversation)


@urlpatterns.route("comments-report/")
def comments_report(request, conversation, **kwargs):
    check_promoted(conversation, request)
    can_view_detail = request.user.has_perm("ej.can_view_report_detail", conversation)
    clusters = get_clusters(conversation)
    clusters_main_comments = [get_cluster_main_comments(cluster) for cluster in clusters]

    return {
        "conversation": conversation,
        "clusters": get_clusters(conversation),
        "clusters_main_comments": clusters_main_comments,
        "can_view_detail": can_view_detail,
        "type_data": "comments-data",
        "groups": get_cluster_names(clusters),
    }


@urlpatterns.route("comments-report/comments-pagination/")
def comments_report_pagination(request, conversation, **kwargs):
    check_promoted(conversation, request)
    clusters = get_clusters(conversation)

    page = request.GET.get("page", 1)
    cards_per_page = request.GET.get("cardsPerPage", 6)
    order_by = request.GET.get("orderBy", OrderByOptions.AGREEMENT)
    sort_order = request.GET.get("sort", "desc")
    cluster_filters = request.GET.get("clusterFilters", ["general"])
    search_string = request.GET.get("searchString", "")

    comments_df = get_comments_dataframe(conversation.comments, "")
    comments_df = filter_comments_by_group(comments_df, clusters, cluster_filters)

    if search_string:
        comments_df = search_comments_df(comments_df, search_string)

    sorted_comments_df = sort_comments_df(comments_df, order_by, sort_order)
    add_id_column(sorted_comments_df)

    comments_dict = sorted_comments_df.to_dict(orient="records")

    paginator = Paginator(comments_dict, cards_per_page)
    comments = get_page(paginator, page)

    return render(
        request,
        "ej_dataviz/report/includes/comment_report/comments-section.jinja2",
        {
            "comments": comments,
            "current_page": comments.number,
            "paginator": paginator,
        },
    )


@urlpatterns.route("votes-over-time/")
def votes_over_time(request, conversation, **kwargs):
    start_date = request.GET.get("startDate")
    end_date = request.GET.get("endDate")
    if start_date and end_date:
        start_date = datetime.date.fromisoformat(start_date)
        end_date = datetime.date.fromisoformat(end_date)
    else:
        return JsonResponse({"error": "end date and start date should be passed as a parameter."})

    if start_date > end_date:
        return JsonResponse({"error": "end date must be gratter then start date."})

    try:
        votes = conversation.time_interval_votes(start_date, end_date)
        return JsonResponse({"data": list(votes)})
    except Exception as e:
        print("Could not generate D3js data")
        print(e)
        return JsonResponse({})


@urlpatterns.route("users/")
def users(request, conversation, **kwargs):
    check_promoted(conversation, request)
    can_view_detail = request.user.has_perm("ej.can_view_report_detail", conversation)
    return {
        "conversation": conversation,
        "type_data": "users-data",
        "can_view_detail": can_view_detail,
    }


# ==============================================================================
# Votes raw data
# ------------------------------------------------------------------------------
@urlpatterns.route("data/votes.<fmt>", perms=["ej.can_view_report_detail"])
def votes_data(request, conversation, fmt, **kwargs):
    check_promoted(conversation, request)
    filename = conversation.slug + "-votes"
    votes = conversation.votes
    return vote_data_common(votes, filename, fmt)


# FIXME: why is <model:cluster> not working?
# adjust conversation_download_data() after fixing this bug
@urlpatterns.route("data/cluster-<int:cluster_id>/votes.<fmt>", perms=["ej.can_view_report_detail"])
def votes_data_cluster(request, conversation, fmt, cluster_id, **kwargs):
    check_promoted(conversation, request)
    cluster = get_cluster_or_404(cluster_id, conversation)
    filename = conversation.slug + f"-{slugify(cluster.name)}-votes"
    return vote_data_common(cluster.votes.all(), filename, fmt)


# ==============================================================================
# Comments raw data
# ------------------------------------------------------------------------------
@urlpatterns.route("data/comments.<fmt>")
def comments_data(request, conversation, fmt, **kwargs):
    check_promoted(conversation, request)
    filename = conversation.slug + "-comments"
    return comments_data_common(conversation.comments, None, filename, fmt)


@urlpatterns.route("data/cluster-<cluster_id>/comments.<fmt>")
def comments_data_cluster(request, conversation, fmt, cluster_id, **kwargs):
    check_promoted(conversation, request)
    cluster = get_cluster_or_404(cluster_id, conversation)
    filename = conversation.slug + f"-{slugify(cluster.name)}-comments"
    return comments_data_common(conversation.comments, cluster.votes, filename, fmt)


# ==============================================================================
# Users raw data
# ------------------------------------------------------------------------------
@urlpatterns.route("data/users.<fmt>")
def users_data(request, conversation, fmt, **kwargs):
    check_promoted(conversation, request)
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
