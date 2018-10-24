import numpy as np
import pandas as pd
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _, ugettext as __
import json

from boogie.router import Router
from boogie.rules import proxy_seq
from ej_clusters.math import get_raw_votes, get_votes
from ej_conversations.models import Conversation
from ej_dataviz import render_dataframe
from ej_math import VoteStats
from hyperpython.components import html_table, hyperlink

from sklearn.decomposition import PCA

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
app_name = 'ej_reports'
conversation_url = '<model:conversation>/reports/'
User = get_user_model()


@urlpatterns.route(conversation_url, login=True)
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
    # Change agree and disagree comments to add up to 100% with skipped
    remaining = 100 - comments['skipped']
    comments['agree'] = 0.01 * comments['agree'] * remaining
    comments['disagree'] = 0.01 * comments['disagree'] * remaining

    # Change agree and disagree participants to add up to 100% with skipped
    remaining = 100 - participants['skipped']
    participants['agree'] = 0.01 * participants['agree'] * remaining
    participants['disagree'] = 0.01 * participants['disagree'] * remaining

    response = {
        'page_title': _('Report'),
        'content_title': hyperlink(conversation),
        'conversation': conversation,
        'statistics': statistics,
        'vote_data': map_to_html_table(statistics['votes']),
        'comment_data': map_to_html_table(statistics['comments']),
        'comments_table': df_to_table(comments),
        'participants_table': df_to_table(participants),
        'clusters': clusters,
    }

    return response


@urlpatterns.route(conversation_url + 'scatter/', login=True)
def scatter(conversation):
    votes = get_votes(conversation)
    votes = votes.where((pd.notnull(votes)), 0.0)

    pca = PCA(n_components=2)
    pca.fit(votes)
    votes_pca = pca.transform(votes)

    # plt.scatter(votes_pca[:, 0], votes_pca[:, 1],
    #             c = ['red', 'green', 'blue'],
    #             edgecolor='none', alpha=0.5,)
    # plt.savefig('foo.png')

    votes_array = votes_pca.tolist()
    js_data = json.dumps(votes_array)

    response = {'plot_data': js_data}
    return response


def file_response(conversation, data_cat, format):
    response = HttpResponse(content_type=f'text/{format}')
    filename = f'filename={conversation.title}_{data_cat}.{format}'
    response['Content-Disposition'] = f'attachment; {filename}'
    return response


def generate_data_file(data, format, response):
    if format == 'json':
        return data.to_json(path_or_buf=response, force_ascii=False)
    elif format == 'csv':
        return data.to_csv(path_or_buf=response, index=False, mode='a')
    elif format == 'msgpack':
        return data.to_msgpack(path_or_buf=response, encoding='utf-8')
    else:
        return


@urlpatterns.route(conversation_url + 'votes.<format>', login=True)
def generate_votes(conversation, format):
    response = file_response(conversation, 'votes', format)
    votes = get_raw_votes(conversation)
    generate_data_file(votes, format, response)
    return response


@urlpatterns.route(conversation_url + 'users.<format>', login=True)
def generate_users(conversation, format):
    response = file_response(conversation, 'users', format)
    votes = get_raw_votes(conversation)
    participants = participants_table(conversation, votes)
    generate_data_file(participants, format, response)
    return response


@urlpatterns.route(conversation_url + 'comments.<format>', login=True)
def generate_comments(conversation, format):
    response = file_response(conversation, 'comments', format)
    votes = get_raw_votes(conversation)
    comments = comments_table(conversation, votes)
    generate_data_file(comments, format, response)
    return response


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
    return np.array(list(data.items())).T


def map_to_html_table(cols):
    array = map_to_table(cols)
    cols, body = array
    cols = [__(col) for col in cols]
    return html_table([body], columns=cols, class_='ReportTable table')


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

    return list(map(transform, data))


def cluster_comments_table(cluster):
    usernames = list(cluster.users.all().values_list('email', flat=True))

    # Filter votes by users present in cluster
    df = cluster.all_votes
    votes = df[df['user'].isin(usernames)]

    data = comments_table(cluster.conversation, votes)
    data = data.sort_values('agree', ascending=False)
    return df_to_table(data)


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

    data = list(User.objects.values_list('email', 'name'))
    participants = pd.DataFrame(list(data), columns=['email', 'name'])
    participants.index = participants.pop('email')

    for col in ['agree', 'disagree', 'skipped', 'divergence']:
        participants[col] = df[col]

    return participants
