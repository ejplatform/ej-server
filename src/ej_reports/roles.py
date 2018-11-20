import numpy as np
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from hyperpython import html

from ej.roles import with_template, html_table
from ej_clusters.math import get_raw_votes
from ej_clusters.models import Cluster
from ej_conversations import models
from ej_dataviz import render_dataframe

User = get_user_model()
DEFAULT_FORMATS = {'csv': 'CSV', 'msgpack': 'MsgPack', 'json': 'JSON'}


#
# Conversation roles
#
@with_template(models.Conversation, role='download-data')
def conversation_download_data(conversation, *, which, formats=DEFAULT_FORMATS, request=None):
    if ':' not in which:
        which = f'report:{which}'

    return {
        'view_name': which,
        'conversation': conversation,
        'formats': formats.items(),
    }


@html.register(models.Conversation, role='stats-table')
def stats_table(conversation, request=None, stats=None, data='votes'):
    if stats is None:
        stats = conversation.statistics()
    cols = stats[data]
    cols, body = np.array(list(cols.items())).T
    cols = [COLUMN_NAMES.get(x, x) for x in cols]
    return html_table([body], columns=cols, class_='ReportTable table')


@html.register(models.Conversation, role='comments-stats-table')
def comments_table(conversation, request=None):
    return df_to_table(conversation.comments_dataframe())


@html.register(models.Conversation, role='participants-stats-table')
def participants_table(conversation, request=None):
    return df_to_table(conversation.participants_dataframe())


#
# Clusters
#
@html.register(Cluster, role='comments-stats-table')
def cluster_comments_table(cluster, request=None, votes=None):
    usernames = list(cluster.users.all().values_list('email', flat=True))
    votes = get_raw_votes(cluster.conversation)

    # Filter votes by users present in cluster
    votes = votes[votes['user'].isin(usernames)]
    data = cluster.conversation.comments_dataframe(votes=votes)
    data = data.sort_values('agree', ascending=False)
    return df_to_table(data)


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


def df_to_table(df, pc=True):
    if pc:
        for col in PC_COLUMNS:
            if col in df:
                df[col] = to_pc(df[col])
    return render_dataframe(df, col_display=COLUMN_NAMES, class_='table long')


def to_pc(data):
    """
    Map floats to percentages.
    """

    def transform(x):
        if isinstance(x, int):
            return str(x)
        elif np.isnan(x):
            return '-'
        else:
            return '%d%%' % x

    return [transform(x) for x in data]
