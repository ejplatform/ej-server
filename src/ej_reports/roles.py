import numpy as np
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _, ugettext as __
from hyperpython import html

from ej.roles import with_template, html_table
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
def stats_table(conversation, request=None):
    statistics = conversation.statistics()
    cols = statistics['votes']
    array = np.array(list(cols.items())).T
    cols, body = array
    cols = [__(col) for col in cols]
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
def cluster_comments_table(cluster):
    usernames = list(cluster.users.all().values_list('email', flat=True))

    # Filter votes by users present in cluster
    df = cluster.all_votes
    votes = df[df['user'].isin(usernames)]
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
