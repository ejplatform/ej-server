from collections import defaultdict
from logging import getLogger
from typing import Callable

from boogie.router import Router
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _, ugettext as __
from ej_dataviz.models import ToolsLinksHelper
from ej_dataviz.routes_report import comments_data_cluster
from sidekick import import_later

from ej_conversations.models import Conversation
from ej_conversations.utils import check_promoted
from ej_clusters.models.clusterization import Clusterization
from ej_tools.utils import get_host_with_schema
from .constants import *
from .utils import (
    get_biggest_cluster,
    get_biggest_cluster_data,
    conversation_has_stereotypes,
    get_stop_words,
)

log = getLogger("ej")
np = import_later("numpy")
wordcloud = import_later("wordcloud")
pd = import_later("pandas")

urlpatterns = Router(
    base_path=f"<model:conversation>/<slug:slug>/",
    template="ej_dataviz/{name}.jinja2",
    models={"conversation": Conversation},
    login=True,
)

app_name = "ej_dataviz"
User = get_user_model()


@urlpatterns.route("dashboard/", perms=["ej.can_view_report:conversation"])
def dashboard(request, conversation, **kwargs):
    check_promoted(conversation, request)
    can_view_detail = request.user.has_perm("ej.can_view_report_detail", conversation)
    statistics = conversation.statistics()
    clusterization = Clusterization.objects.filter(conversation=conversation)
    host = get_host_with_schema(request)
    names = getattr(settings, "EJ_PROFILE_FIELD_NAMES", {})
    biggest_cluster_data = get_dashboard_biggest_cluster(request, conversation, clusterization)
    return {
        "conversation": conversation,
        "can_view_detail": can_view_detail,
        "statistics": statistics,
        "conversation_has_stereotypes": conversation_has_stereotypes(clusterization),
        "bot": ToolsLinksHelper.get_bot_link(host),
        "json_data": clusters(request, conversation),
        "biggest_cluster_data": biggest_cluster_data,
        "gender_field": names.get("gender", _("Gender")),
        "race_field": names.get("race", _("Race")),
        "conversation": check_promoted(conversation, request),
        "pca_link": _("https://en.wikipedia.org/wiki/Principal_component_analysis"),
    }


@urlpatterns.route("scatter/")
def scatter(request, conversation, **kwargs):
    names = getattr(settings, "EJ_PROFILE_FIELD_NAMES", {})
    return {
        "gender_field": names.get("gender", _("Gender")),
        "race_field": names.get("race", _("Race")),
        "conversation": check_promoted(conversation, request),
        "pca_link": _("https://en.wikipedia.org/wiki/Principal_component_analysis"),
    }


@urlpatterns.route("scatter/pca.json", template=None)
def scatter_pca_json(request, conversation, **kwargs):
    from sklearn.decomposition import PCA
    from sklearn import impute

    check_promoted(conversation, request)
    kwargs = {}
    clusterization = getattr(conversation, "clusterization", None)
    if clusterization is not None:
        clusterization.update_clusterization()

    df = conversation.votes.votes_table("mean")
    if df.shape[0] <= 3 or df.shape[1] <= 3:
        return JsonResponse({"error": "InsufficientData", "message": _("Not enough data")})
    pca = PCA(2)
    data = pca.fit_transform(df.values)
    data = pd.DataFrame(data, index=df.index, columns=["x", "y"])
    imputer = impute.SimpleImputer().fit(df.values)

    # Mark self, if found
    if request.user.id in data.index:
        user_coords = data.loc[request.user.id]
    else:
        user_coords = [0, 0]

    # Add extra columns (for now it is hardcoded as name, gender and race)
    # In the future, it might be configurable.
    extra_fields = ["name", "gender", "race", "state"]
    kwargs["extra_fields"] = extra_fields
    data[extra_fields] = User.objects.filter(id__in=data.index).dataframe(
        *(FIELD_DATA[f]["query"] for f in extra_fields)
    )
    for f in extra_fields:
        data[f] = FIELD_DATA[f].get("transform", lambda x: x)(data[f])

    # Check clusters
    stereotype_coords = list(
        create_stereotype_coords(
            conversation,
            data,
            list(df.columns),
            transformer=lambda x: pca.transform(imputer.transform(x)),
            kwargs=kwargs,
        )
    )
    return format_echarts_option(data, user_coords, stereotype_coords, **kwargs)


@urlpatterns.route("scatter/group-<groupby>.json")
def scatter_group(request, conversation, groupby, **kwargs):
    if groupby not in VALID_GROUP_BY:
        return JsonResponse({"error": "AttributeError", "message": "invalid groupby parameter"})
    param = VALID_GROUP_BY[groupby]

    # Process raw data to form clusters
    data_pairs = User.objects.filter(votes__comment__conversation=conversation).values_list("id", param)

    data = defaultdict(list)
    for user, value in data_pairs:
        data[value].append(user)

    name_transform = GROUP_NAMES[groupby]
    description_transform = GROUP_DESCRIPTIONS[groupby]
    return JsonResponse(
        {
            "groups": {name_transform(k): v for k, v in data.items()},
            "descriptions": {name_transform(k): description_transform(k) for k in data},
            "groupby": groupby,
        }
    )


@urlpatterns.route("dashboard/words.json")
def words(request, conversation, **kwargs):
    data = "\n".join(conversation.approved_comments.values_list("content", flat=True))
    regexp = r"\w[\w'\u0327]+"
    wc = wordcloud.WordCloud(stopwords=get_stop_words(), regexp=regexp)
    cloud = sorted(wc.process_text(data).items(), key=lambda x: -x[1])[:50]
    return JsonResponse({"cloud": cloud})


#
# Auxiliary functions
#
def create_stereotype_coords(conversation, table, comments: list, transformer: Callable, kwargs: dict):
    if apps.is_installed("ej_clusters") and getattr(conversation, "clusterization", None):
        from ej_clusters.models import Stereotype

        labels = conversation.clusterization.clusters.all().dataframe("name", index="users")
        if labels.shape != (0, 0):
            table["cluster"] = labels.loc[labels.index.values != None]
            table["cluster"].fillna(__("*Unknown*"), inplace=True)
            kwargs["labels"] = labels

            # Stereotype votes
            stereotypes = conversation.clusters.all().stereotypes()
            names = dict(Stereotype.objects.values_list("id", "name"))
            votes_ = stereotypes.votes_table()
            missing_cols = set(comments) - set(votes_.columns)
            for col in missing_cols:
                votes_[col] = float("nan")
            votes_ = votes_[comments]
            points = transformer(votes_)

            for pk, (x, y) in zip(votes_.index, points):
                yield {
                    "name": names[pk],
                    "symbol": "circle",
                    "coord": [x, y, names[pk], None, None],
                    "label": {"show": True, "formatter": names[pk], "color": "black"},
                    "itemStyle": {"opacity": 0.75, "color": "rgba(180, 180, 180, 0.33)"},
                    "tooltip": {"formatter": _("{} persona").format(names[pk])},
                }


def format_echarts_option(data, user_coords, stereotype_coords, extra_fields: list, labels=None):
    """
    Format option JSON for echarts.
    """
    visual_map = [
        {"dimension": n, **FIELD_DATA[f]["visual_map"]} for n, f in enumerate(extra_fields[1:], 3)
    ]
    if labels is not None:
        clusters = [*pd.unique(labels.values.flat), _("*Unknown*")]
        visual_map.append(
            {
                **PIECEWISE_OPTIONS,
                "dimension": len(visual_map) + 3,
                "categories": clusters,
                "inRange": {"color": COLORS[: len(clusters)]},
            }
        )

    axis_opts = {"axisTick": {"show": False}, "axisLabel": {"show": False}}
    return JsonResponse(
        {
            "option": {
                "tooltip": {
                    "showDelay": 0,
                    "axisPointer": {
                        "show": True,
                        "type": "cross",
                        "lineStyle": {"type": "dashed", "width": 1},
                    },
                },
                "xAxis": axis_opts,
                "yAxis": axis_opts,
                "series": [
                    {
                        "type": "scatter",
                        "name": _("PCA data"),
                        "symbolSize": 18,
                        "markPoint": {
                            "data": [
                                {
                                    "name": _("You!"),
                                    "coord": [*user_coords, _("You!"), None, None],
                                    "label": {"show": True, "formatter": _("You!")},
                                    "itemStyle": {"color": "black"},
                                    "tooltip": {"formatter": _("You!")},
                                },
                                *stereotype_coords,
                            ]
                        },
                        "data": data.values.tolist(),
                    }
                ],
                "grid": {"left": 10, "right": 10, "top": 10, "bottom": 30},
            },
            "visualMap": visual_map,
        }
    )


def clusters(request, conversation):
    """
    Returns the cluster data as json format to render groups on frontend.
    """
    from ej_clusters.routes import index

    clusters_data = index(request, conversation)
    clusters_shapes = clusters_data.get("json_data")
    return clusters_shapes


def get_dashboard_biggest_cluster(request, conversation, clusterization):
    biggest_cluster = get_biggest_cluster(clusterization)
    if biggest_cluster:
        biggest_cluster_df = comments_data_cluster(request, conversation, None, biggest_cluster.id)
        return get_biggest_cluster_data(biggest_cluster, biggest_cluster_df)
    return {}
