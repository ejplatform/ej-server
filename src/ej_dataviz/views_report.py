from functools import lru_cache
import datetime

from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.text import slugify
from django.utils.translation import gettext as _, gettext_lazy
from sidekick import import_later
from django.core.paginator import Paginator

from ej_conversations.models import Conversation
from ej_conversations.utils import check_promoted
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
    vote_data_common,
    OrderByOptions,
)

from ej.decorators import can_access_dataviz, can_view_report_details

pd = import_later("pandas")


@can_access_dataviz
def comments_report(request, conversation_id, **kwargs):
    conversation = Conversation.objects.get(pk=conversation_id)
    check_promoted(conversation, request)
    can_view_detail = request.user.has_perm("ej.can_view_report_detail", conversation)
    clusters = get_clusters(conversation)
    clusters_main_comments = [get_cluster_main_comments(cluster) for cluster in clusters]

    return render(
        request,
        "ej_dataviz/report/comments-report.jinja2",
        {
            "conversation": conversation,
            "clusters": get_clusters(conversation),
            "clusters_main_comments": clusters_main_comments,
            "can_view_detail": can_view_detail,
            "type_data": "comments-data",
            "groups": get_cluster_names(clusters),
        },
    )


@can_access_dataviz
def comments_report_pagination(request, conversation_id, **kwargs):
    conversation = Conversation.objects.get(pk=conversation_id)
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


@can_access_dataviz
def votes_over_time(request, conversation_id, **kwargs):
    from django.utils.timezone import make_aware

    conversation = Conversation.objects.get(pk=conversation_id)
    start_date = request.GET.get("startDate")
    end_date = request.GET.get("endDate")
    if start_date and end_date:
        start_date = make_aware(datetime.datetime.fromisoformat(start_date))  # convert js naive date
        end_date = make_aware(datetime.datetime.fromisoformat(end_date))  # # convert js naive date
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


@can_access_dataviz
def users(request, conversation_id, **kwargs):
    conversation = Conversation.objects.get(pk=conversation_id)
    check_promoted(conversation, request)
    can_view_detail = request.user.has_perm("ej.can_view_report_detail", conversation)

    return render(
        request,
        "ej_dataviz/report/users.jinja2",
        {
            "conversation": conversation,
            "type_data": "users-data",
            "can_view_detail": can_view_detail,
        },
    )


# ==============================================================================
# Votes raw data
# ------------------------------------------------------------------------------
@can_view_report_details
def votes_data(request, conversation, fmt, **kwargs):
    check_promoted(conversation, request)
    filename = conversation.slug + "-votes"
    votes = conversation.votes
    return vote_data_common(votes, filename, fmt)


# FIXME: why is <model:cluster> not working?
# adjust conversation_download_data() after fixing this bug
@can_view_report_details
def votes_data_cluster(request, conversation, fmt, cluster_id, **kwargs):
    if not request.user.has_perm("ej.can_view_report_detail", conversation):
        return JsonResponse({"error": "You don't have permission to view this data."})
    check_promoted(conversation, request)
    cluster = get_cluster_or_404(cluster_id, conversation)
    filename = conversation.slug + f"-{slugify(cluster.name)}-votes"
    return vote_data_common(cluster.votes.all(), filename, fmt)


# ==============================================================================
# Comments raw data
# ------------------------------------------------------------------------------

# ==============================================================================
# Users raw data
# ------------------------------------------------------------------------------
@can_access_dataviz
def users_data(request, conversation_id, fmt, **kwargs):
    conversation = Conversation.objects.get(pk=conversation_id)
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
    _ = gettext_lazy
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
