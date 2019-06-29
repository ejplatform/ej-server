from boogie.router import Router
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from sidekick import import_later

from ej_conversations.models import Conversation
from ej_conversations.routes import conversation_url
from ej_conversations.utils import check_promoted
from .routes import EXPOSED_PROFILE_FIELDS

pd = import_later('pandas')

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
    columns = "author__email", "author__id", "comment__content", "comment__id", "choice"
    df = conversation.votes.dataframe(*columns)
    df.columns = "email", "author", "comment", "comment_id", "choice"
    df.choice = list(map({-1: 'disagree', 1: 'agree', 0: 'skip'}.get, df['choice']))
    return data_response(df, fmt, filename)


@urlpatterns.route("data/comments.<fmt>")
def comments_data(request, conversation, fmt, slug, check=check_promoted):
    check(conversation, request)
    filename = conversation.slug + "-comments"
    df = conversation.comments.statistics_summary_dataframe()
    conversation.comments.extend_dataframe(df, "id", "author__email", "author__id")

    # Adjust column names
    columns = [
        "content",
        "id",
        "author__email",
        "author__id",
        "agree",
        "disagree",
        "skipped",
        "divergence",
        "participation",
    ]
    df = df[columns]
    df.columns = ["comment", "comment_id", "author", "author_id", *columns[4:]]
    return data_response(df, fmt, filename)


@urlpatterns.route("data/users.<fmt>")
def users_data(request, conversation, fmt, slug, check=check_promoted):
    check(conversation, request)
    filename = conversation.slug + "-users"

    df = conversation.users.statistics_summary_dataframe(
        extend_fields=('id', *EXPOSED_PROFILE_FIELDS),
    )
    df = df[[
        'email',
        'id',
        'name',
        *EXPOSED_PROFILE_FIELDS,
        'agree', 'disagree', 'skipped', 'divergence', 'participation',
    ]]
    df.columns = ['email', 'user_id', *df.columns[2:]]
    return data_response(df, fmt, filename)


#
# Auxiliary functions
#
def data_response(data: pd.DataFrame, fmt: str, filename: str):
    response = HttpResponse(content_type=f"text/{fmt}")
    filename = f"filename={filename}.{fmt}"
    response["Content-Disposition"] = f"attachment; {filename}"
    if fmt == "json":
        data.to_json(path_or_buf=response, force_ascii=False)
    elif fmt == "csv":
        data.to_csv(path_or_buf=response, index=False, mode="a", float_format="%.3f")
    elif fmt == "msgpack":
        data.to_msgpack(path_or_buf=response, encoding="utf-8")
    else:
        raise ValueError(f"invalid format: {fmt}")
    return response
