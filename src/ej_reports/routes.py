from django.contrib.auth import get_user_model
from django.http import HttpResponse, Http404
from django.utils.translation import ugettext_lazy as _

from boogie.router import Router
from boogie.rules import proxy_seq
from ej_clusters.math import get_raw_votes
from ej_conversations.models import Conversation
from ej_dataviz.routes import comments_table, participants_table, \
    generate_scatter, df_to_table, map_to_html_table, cluster_comments_table
from hyperpython.components import hyperlink


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


@urlpatterns.route(conversation_url)
def index(request, conversation):
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

    return {
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


@urlpatterns.route(conversation_url + 'scatter/')
def scatter(request, conversation):
    return generate_scatter(request, conversation)


def file_response(conversation, data_cat, format):
    response = HttpResponse(content_type=f'text/{format}')
    filename = f'filename={conversation.title}_{data_cat}.{format}'
    response['Content-Disposition'] = f'attachment; {filename}'
    return response


def generate_data_file(data, format, response,
                       options={
                           'json': {'force_ascii': False},
                           'csv': {'index': False, 'mode': 'a'},
                           'msgpack': {'encoding': 'utf-8'}, }):
    kwargs = options[format]
    return getattr(data, f'to_{format}')(path_or_buf=response, **kwargs)


@urlpatterns.route(conversation_url + '<action>.<format>')
def generate_action(conversation, action, format):
    response = file_response(conversation, action, format)
    votes = get_raw_votes(conversation)
    if action == 'votes':
        data = votes
    elif action == 'users':
        data = participants_table(conversation, votes)
    elif action == 'comments':
        data = comments_table(conversation, votes)
    else:
        raise Http404
    generate_data_file(data, format, response)
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
