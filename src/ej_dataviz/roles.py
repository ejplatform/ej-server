from django.apps import apps
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from hyperpython import html, div
from hyperpython.components import html_table, html_map, fa_icon
from sidekick import import_later

from ej.roles import with_template
from ej_conversations import models

np = import_later("numpy")
User = get_user_model()


#
# Conversation roles
#
@with_template(models.Conversation, role="download-data")
def conversation_download_data(conversation, *, which, formats=None, cluster=None, **url_kwargs):
    if ":" not in which:
        which = f"report:{which}"
        if cluster is not None:
            which += "-cluster"

    # Prepare urls
    url_kwargs = {}
    if cluster is not None:
        url_kwargs["cluster_id"] = cluster.id

    format_lst = []
    for format, name in (formats or DEFAULT_FORMATS).items():
        url = conversation.url(which, fmt=format, **url_kwargs)
        format_lst.append((format, name, url))

    return {"conversation": conversation, "formats": format_lst}


@html.register(models.Conversation, role="stats-table")
def stats_table(conversation, stats=None, data="votes", request=None, **kwargs):
    if stats is None:
        stats = conversation.statistics()

    get = COLUMN_NAMES.get
    return div([html_map({get(k, k): v}) for k, v in stats[data].items()], **kwargs).add_class(
        "stat-slab", first=True
    )


@html.register(models.Conversation, role="comments-stats-table")
def comments_table(conversation, request=None, **kwargs):
    data = conversation.comments.statistics_summary_dataframe(normalization=100)
    data = data.sort_values("agree", ascending=False)
    return prepare_dataframe(data, pc=True)


@html.register(models.Conversation, role="participants-stats-table")
def participants_table(conversation, **kwargs):
    data = conversation.users.statistics_summary_dataframe(normalization=100, convergence=False)
    data = data.sort_values("agree", ascending=False)
    return prepare_dataframe(data, pc=True)


#
# Clusters
#
if apps.is_installed("ej_clusters"):
    from ej_clusters.models import Cluster

    @html.register(Cluster, role="comments-stats-table")
    def cluster_comments_table(cluster, **kwargs):
        data = cluster.comments_statistics_summary_dataframe(normalization=100)
        data = data.sort_values("agree", ascending=False)
        return prepare_dataframe(data, pc=True)


#
# Auxiliary functions
#
def prepare_dataframe(df, pc=False):
    """
    Renders dataframe in a HTML table.
    """
    if pc is True:
        df = df.copy()
        for col, data in df.items():
            if data.dtype == float:
                df[col] = data.apply(lambda x: "-" if np.isnan(x) else "%d%%" % x)
    return render_dataframe(df, col_display=TABLE_COLUMN_NAMES, class_="table long text-6")


def render_dataframe(df, index=False, *, col_display=None, **kwargs):
    """
    Convert a Pandas dataframe to a hyperpython structure.

    Args:
        df (DataFrame):
            Input data frame.
        col_display (map):
            An optional mapping from column names in a dataframe to their
            corresponding human friendly counterparts.
        index (bool):
            If given, add index as the first column.

    Additional attributes (such as class, id, etc) can be passed as keyword
    arguments.
    """
    data = np.array(df.astype(object))
    columns = df.columns

    if index:
        data = np.hstack([df.index[:, None], df])
        columns = [df.index.name or "index", *columns]

    if col_display:
        columns = [col_display.get(x, x) for x in columns]
    return html_table(data, columns=columns, style="width: 100%", **kwargs)


#
# Constants
#

# TODO: make list of formats configurable
# "msgpack": "MsgPack"
DEFAULT_FORMATS = {
    "xlsx": "Excel", 
    "csv": "CSV", 
    "json": "JSON"
}

COLUMN_NAMES = {
    "agree": _("Agree"),
    "author": _("Author"),
    "approved": _("Approved"),
    "average": _("Average"),
    "comment": _("Comment"),
    "content": _("Comment"),
    "convergence": _("Convergence"),
    "disagree": _("Disagree"),
    "divergence": _("Divergence"),
    "entropy": _("Entropy"),
    "missing": _("Missing"),
    "name": _("Name"),
    "participation": _("Participation ratio"),
    "pending": _("Pending"),
    "rejected": _("Rejected"),
    "skip": _("Skip"),
    "skipped": _("Skipped"),
    "text": _("Text"),
    "total": _("Total"),
    "user": _("User"),
    "votes": _("Votes"),
}

TABLE_COLUMN_NAMES = {
    **COLUMN_NAMES,
    "agree": fa_icon("check", title=_("Agree")),
    "convergence": fa_icon(
        "handshake",
        title=_("Agreement level\n0%: votes are evenly split\n100%: everyone has the same opinion"),
    ),
    "disagree": fa_icon("times", title=_("Disagree")),
    "participation": fa_icon("users", title=_("Participation ratio")),
    "skip": fa_icon("arrow-right", title=_("Skip")),
    "skipped": fa_icon("arrow-right", title=_("Skipped")),
}

PC_COLUMNS = [
    "missing",
    "skipped",
    "agree",
    "disagree",
    "average",
    "convergence",
    "entropy",
    "participation",
]

html.register(type(fa_icon("check")), lambda x, *args: x)
