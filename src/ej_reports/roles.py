from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from hyperpython import html
from hyperpython.components import html_table
from sidekick import import_later

from ej.roles import with_template
from ej_clusters.models import Cluster
from ej_conversations import models

np = import_later('numpy')

User = get_user_model()
DEFAULT_FORMATS = {'csv': 'CSV', 'msgpack': 'MsgPack', 'json': 'JSON'}


#
# Conversation roles
#
@with_template(models.Conversation, role='download-data')
def conversation_download_data(conversation, *, which, formats=DEFAULT_FORMATS, **kwargs):
    if ':' not in which:
        which = f'report:{which}'

    return {
        'view_name': which,
        'conversation': conversation,
        'formats': formats.items(),
    }


@html.register(models.Conversation, role='stats-table')
def stats_table(conversation, stats=None, data='votes', **kwargs):
    if stats is None:
        stats = conversation.statistics()
    cols = stats[data]
    cols, body = np.array(list(cols.items())).T
    cols = [COLUMN_NAMES.get(x, x) for x in cols]
    return html_table([body], columns=cols, class_='ReportTable table')


@html.register(models.Conversation, role='comments-stats-table')
def comments_table(conversation, **kwargs):
    data = conversation.comments.statistics_summary_dataframe(normalization=100)
    data = data.sort_values('agree', ascending=False)
    return prepare_dataframe(data, pc=True)


@html.register(models.Conversation, role='participants-stats-table')
def participants_table(conversation, **kwargs):
    data = conversation.users.statistics_summary_dataframe(normalization=100)
    data = data.sort_values('agree', ascending=False)
    return prepare_dataframe(data, pc=True)


#
# Clusters
#
@html.register(Cluster, role='comments-stats-table')
def cluster_comments_table(cluster, **kwargs):
    data = cluster.comments_statistics_summary_dataframe(normalization=100)
    data = data.sort_values('agree', ascending=False)
    return prepare_dataframe(data, pc=True)


#
# Auxiliary functions
#
COLUMN_NAMES = {
    'author': _('Author'),
    'text': _('Text'),
    'votes': _('Votes'),
    'missing': _('Missing'),
    'skipped': _('Skipped'),
    'agree': _('Agree'),
    'disagree': _('Disagree'),
    'average': _('Average'),
    'divergence': _('Divergence'),
    'entropy': _('Entropy'),
    'comment': _('Comment'),
    'user': _('User'),
    'participation': _('Participation ratio'),
    'name': _('Name'),
    'total': _('Total'),
    'skip': _('Skip'),
    'approved': _('Approved'),
    'rejected': _('Rejected'),
    'pending': _('Pending'),
}
PC_COLUMNS = [
    'missing', 'skipped', 'agree', 'disagree', 'average',
    'divergence', 'entropy', 'participation',
]


def prepare_dataframe(df, pc=False):
    """
    Renders dataframe in a HTML table.
    """
    if pc is True:
        df = df.copy()
        for col, data in df.items():
            if data.dtype == float:
                df[col] = data.apply(lambda x: '-' if np.isnan(x) else '%d%%' % x)
    return render_dataframe(df, col_display=COLUMN_NAMES, class_='table long')


def render_dataframe(df, index=False, *, datatable=False, class_=(),
                     col_display=None, **kwargs):
    """
    Convert a Pandas dataframe to a hyperpython structure.

    Args:
        df (DataFrame):
            Input data frame.
        col_display (map):
            An optional mapping from column names in a dataframe to their
            corresponding human friendly counterparts.
        datatable (bool):
            If True, prepare data to be handled by the Data table js library.
        index (bool):
            If given, add index as the first column.

    Additional attributes (such as class, id, etc) can be passed as keyword
    arguments.
    """
    if datatable:
        class_ = [*class_, 'display', 'cell-border', 'compact']

    data = np.array(df.astype(object))
    columns = df.columns

    if index:
        data = np.hstack([df.index[:, None], df])
        columns = [df.index.name or 'index', *columns]

    columns = as_display_values(columns, col_display)
    return html_table(data, columns=columns, class_=class_, **kwargs)


def as_display_values(seq, translations=None):
    if translations is None:
        return list(map(str, seq))
    else:
        return [str(translations.get(x, x)) for x in seq]
