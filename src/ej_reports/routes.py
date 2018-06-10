import numpy as np
from django.utils.translation import ugettext_lazy as _, ugettext as __

from boogie.router import Router
from hyperpython.components import html_table, hyperlink

from ej_clusters.math import get_raw_votes
from ej_conversations.models import Conversation
from ej_dataviz import render_dataframe
from ej_math import VoteStats

app_name = 'ej_reports'
urlpatterns = Router(
    template=['ej_reports/{name}.jinja2', 'generic.jinja2'],
    perms=['ej_reports.can_view_report'],
    object='conversation',
    models={
        'conversation': Conversation,
    },
    lookup_field='slug',
    lookup_type='slug',
    login=True,
)
conversation_url = '<model:conversation>/reports/'


@urlpatterns.route(conversation_url)
def index(conversation):
    statistics = conversation.statistics()
    votes = get_raw_votes(conversation)
    math = VoteStats(votes)
    print(votes)
    return {
        'title': _('Report'),
        'content_title': hyperlink(conversation),
        'conversation': conversation,
        'statistics': statistics,
        'vote_data': map_to_table(statistics['votes']),
        'comment_data': map_to_table(statistics['comments']),
        'comments_table': df_to_table(math.comments(pc=True)),
        'participants_table': df_to_table(math.users(pc=True)),
    }


@urlpatterns.route(conversation_url + 'clusters/')
def clusters(conversation):
    return {
        'conversation': conversation,
    }


@urlpatterns.route(conversation_url + 'radar/')
def radar(conversation):
    return {
        'conversation': conversation,
    }


@urlpatterns.route(conversation_url + 'divergence/')
def divergence(conversation):
    return {
        'conversation': conversation,
    }


#
# Auxiliary functions and data
#
COLUMN_NAMES = {
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
}
PC_COLUMNS = [
    'votes', 'missing', 'skipped', 'agree', 'disagree', 'average',
    'divergence', 'entropy',
]


def map_to_table(data):
    array = np.array(list(data.items())).T
    cols, body = array
    return html_table([body], columns=[__(col) for col in cols], class_='ReportTable')


def df_to_table(df, pc=True):
    if pc:
        for col in PC_COLUMNS:
            if col in df:
                df[col] = to_pc(df[col])
    return render_dataframe(df, col_display=COLUMN_NAMES)


def to_pc(data):
    def transform(x):
        if isinstance(x, int):
            return str(x)
        elif np.isnan(x):
            return '-'
        else:
            return '%d%%' % x

    return list(map(transform, data))
