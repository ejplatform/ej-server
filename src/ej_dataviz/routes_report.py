from django.contrib.auth import get_user_model
from django.http import HttpResponse

from boogie.router import Router
from ej_conversations.models import Conversation
from ej_conversations.routes import conversation_url
from ej_conversations.utils import check_promoted
from .routes import EXPOSED_PROFILE_FIELDS

urlpatterns = Router(
    base_path=conversation_url + "reports/",
    template="ej_dataviz/report/{name}.jinja2",
    models={"conversation": Conversation},
    login=True,
    perms=["ej.can_view_report_detail:conversation"],
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


@urlpatterns.route("users/")
def users(request, conversation, slug, check=check_promoted):
    return {"conversation": check(conversation, request)}


#
# Raw data
#
@urlpatterns.route("data/votes.<fmt>")
def votes_data(request, conversation, fmt, slug, check=check_promoted):
    check(conversation, request)
    filename = conversation.slug + "-votes"
    data = conversation.votes.dataframe()
    return data_response(data, fmt, filename)


@urlpatterns.route("data/comments.<fmt>")
def comments_data(request, conversation, fmt, slug, check=check_promoted):
    check(conversation, request)
    filename = conversation.slug + "-comments"
    data = conversation.comments.statistics_summary_dataframe()
    return data_response(data, fmt, filename)


@urlpatterns.route("data/users.<fmt>")
def users_data(request, conversation, fmt, slug, check=check_promoted):
    check(conversation, request)
    filename = conversation.slug + "-users"
    data = conversation.users.statistics_summary_dataframe(
        extend_fields=EXPOSED_PROFILE_FIELDS
    )
    return data_response(data, fmt, filename)


#
# Auxiliary functions
#
def data_response(data, fmt, filename):
    response = HttpResponse(content_type=f"text/{format}")
    filename = f"filename={filename}.{format}"
    response["Content-Disposition"] = f"attachment; {filename}"
    if fmt == "json":
        data.to_json(path_or_buf=response, force_ascii=False)
    elif fmt == "csv":
        data.to_csv(path_or_buf=response, index=False, mode="a")
    elif fmt == "msgpack":
        data.to_msgpack(path_or_buf=response, encoding="utf-8")
    else:
        raise ValueError(f"invalid format: {format}")
    return response
