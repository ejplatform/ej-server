import numpy as np
import pandas as pd
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _, ugettext as __

from boogie.router import Router
from boogie.rules import proxy_seq
from ej_clusters.math import get_raw_votes
from ej_conversations.models import Conversation
from ej_dataviz import render_dataframe
from ej_math import VoteStats
from hyperpython.components import html_table, hyperlink

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
User = get_user_model()


@urlpatterns.route(conversation_url)
def index(conversation):
    statistics = conversation.statistics()
    votes = get_raw_votes(conversation)
    comments = comments_table(conversation, votes)
    participants = participants_table(conversation, votes)
    clusters = proxy_seq(
        conversation.clusters.all(),
        all_votes=votes,
        comment_table=cluster_comments_table,
        size=lambda x: x.users.count(),
    )

    return {
        'title': _('Report'),
        'content_title': hyperlink(conversation),
        'conversation': conversation,
        'statistics': statistics,
        'vote_data': map_to_table(statistics['votes']),
        'comment_data': map_to_table(statistics['comments']),
        'comments_table': df_to_table(comments),
        'participants_table': df_to_table(participants),
        'clusters': clusters,
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


def map_to_table(data):
    array = np.array(list(data.items())).T
    cols, body = array
    return html_table([body], columns=[__(col) for col in cols], class_='ReportTable table')


def df_to_table(df, pc=True):
    if pc:
        for col in PC_COLUMNS:
            if col in df:
                df[col] = to_pc(df[col])
    return render_dataframe(df, col_display=COLUMN_NAMES, class_='table long')


def to_pc(data):
    def transform(x):
        if isinstance(x, int):
            return str(x)
        elif np.isnan(x):
            return '-'
        else:
            return '%d%%' % x

    return list(map(transform, data))


def cluster_comments_table(cluster):
    usernames = list(cluster.users.all().values_list('username', flat=True))

    # Filter votes by users present in cluster
    df = cluster.all_votes
    votes = df[df['user'].isin(usernames)]
    return df_to_table(comments_table(cluster.conversation, votes))


def comments_table(conversation, votes):
    """
    Data frame with information about each comment in conversation.
    """

    stats = VoteStats(votes)
    df = stats.comments(pc=True)
    comments = conversation.comments.approved().display_dataframe()
    comments = comments[['author', 'text']]
    for col in ['agree', 'disagree', 'skipped', 'divergence']:
        comments[col] = df[col]
    comments['participation'] = 100 - df['missing']
    comments.dropna(inplace=True)
    return comments


def participants_table(conversation, votes):
    """
    Data frame with information about each participant in conversation.
    """

    stats = VoteStats(votes)
    df = stats.users(pc=True)

    data = list(User.objects.values_list('username', 'name'))
    participants = pd.DataFrame(list(data), columns=['username', 'name'])
    participants.index = participants.pop('username')

    for col in ['agree', 'disagree', 'skipped', 'divergence']:
        participants[col] = df[col]

    return participants
