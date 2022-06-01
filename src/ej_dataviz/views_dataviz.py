from collections import defaultdict
from logging import getLogger
from typing import Callable

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect, reverse
from django.utils.translation import gettext as __, gettext_lazy as _
from ej.decorators import can_access_dataviz
from ej_clusters.models.clusterization import Clusterization
from ej_conversations.models import Conversation
from ej_conversations.utils import check_promoted
from ej_dataviz.models import ToolsLinksHelper
from ej_signatures.models import SignatureFactory
from ej_tools.utils import get_host_with_schema
from sidekick import import_later

from .constants import *
from .utils import (
    clusters,
    conversation_has_stereotypes,
    create_stereotype_coords,
    format_echarts_option,
    get_dashboard_biggest_cluster,
    get_stop_words,
)

log = getLogger("ej")
np = import_later("numpy")
wordcloud = import_later("wordcloud")
pd = import_later("pandas")

app_name = "ej_dataviz"
User = get_user_model()


@can_access_dataviz
def index(request, conversation_id, **kwargs):
    conversation = Conversation.objects.get(id=conversation_id)
    check_promoted(conversation, request)
    can_view_detail = request.user.has_perm("ej.can_view_report_detail", conversation)
    statistics = conversation.statistics()
    clusterization = Clusterization.objects.filter(conversation=conversation)
    host = get_host_with_schema(request)
    names = getattr(settings, "EJ_PROFILE_FIELD_NAMES", {})
    biggest_cluster_data = get_dashboard_biggest_cluster(request, conversation, clusterization)

    render_context = {
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

    return render(request, "ej_dataviz/dashboard.jinja2", render_context)


@can_access_dataviz
def communication(request, conversation_id, **kwargs):
    import os

    conversation = Conversation.objects.get(id=conversation_id)
    author = conversation.author
    user_signature = SignatureFactory.get_user_signature(author)
    tool = user_signature.get_tool(_("Rocket.Chat"), conversation)
    host = get_host_with_schema(request)
    dashboard_route = reverse("boards:dataviz-dashboard", kwargs=conversation.get_url_kwargs())
    if tool.is_active:
        context = {
            "conversation": conversation,
            "ROCKETCHAT_HOST": os.getenv("ROCKETCHAT_HOST"),
            "dashboard_location": f"{host}{dashboard_route}",
        }
        return render(request, "ej_dataviz/communication.jinja2", context)
    return redirect("boards:signatures-upgrade", board_slug=conversation.board.slug)


@can_access_dataviz
def scatter(request, conversation_id, **kwargs):
    conversation = Conversation.objects.get(id=conversation_id)
    names = getattr(settings, "EJ_PROFILE_FIELD_NAMES", {})
    render_context = {
        "gender_field": names.get("gender", _("Gender")),
        "race_field": names.get("race", _("Race")),
        "conversation": check_promoted(conversation, request),
        "pca_link": _("https://en.wikipedia.org/wiki/Principal_component_analysis"),
    }

    return render(request, "ej_dataviz/scatter.jinja2", render_context)


@can_access_dataviz
def scatter_pca_json(request, conversation_id, **kwargs):
    from sklearn.decomposition import PCA
    from sklearn import impute

    conversation = Conversation.objects.get(id=conversation_id)
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


@can_access_dataviz
def scatter_group(request, conversation_id, groupby, **kwargs):
    conversation = Conversation.objects.get(id=conversation_id)

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


@can_access_dataviz
def words(request, conversation_id, **kwargs):
    conversation = Conversation.objects.get(id=conversation_id)
    data = "\n".join(conversation.approved_comments.values_list("content", flat=True))
    regexp = r"\w[\w'\u0327]+"
    wc = wordcloud.WordCloud(stopwords=get_stop_words(), regexp=regexp)
    cloud = sorted(wc.process_text(data).items(), key=lambda x: -x[1])[:50]
    return JsonResponse({"cloud": cloud})
