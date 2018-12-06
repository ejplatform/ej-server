import json

from django.contrib.auth import get_user_model
from django.http import HttpResponse

from boogie.router import Router
from ej_conversations.models import Conversation

urlpatterns = Router(
    template=['ej_reports/{name}.jinja2', 'generic.jinja2'],
    models={'conversation': Conversation},
    lookup_field='slug',
    lookup_type='slug',
    login=True,
    perms=['ej.can_view_report_detail:conversation']
)
app_name = 'ej_reports'
reports_url = '<model:conversation>/reports/'
User = get_user_model()


#
# Base report URLs
#
@urlpatterns.route(reports_url, perms=[])
def index(request, conversation):
    user = request.user
    can_download_data = can_see_participants = \
        user.has_perm('ej.can_edit_conversation', conversation)

    clusterization = conversation.get_clusterization(None)
    statistics = conversation.statistics()
    if clusterization:
        clusterization.update_clusterization()
        clusters = clusterization.clusters.all()
    else:
        clusters = ()

    return {
        'clusters': clusters,
        'conversation': conversation,
        'users': statistics['participants']['voters'],
        'can_download_data': can_download_data,
        'can_see_participants': can_see_participants,
    }


@urlpatterns.route(reports_url + 'scatter/', perms=[])
def scatter(conversation):
    return {'conversation': conversation}


@urlpatterns.route(reports_url + 'scatter/pca.json', perms=[])
def scatter_pca_json(conversation):
    df = conversation.votes.pca_reduction()
    return {'votes': json.dumps(df.tolist())}


@urlpatterns.route(reports_url + 'participants/')
def participants_table(conversation):
    return {'conversation': conversation}


#
# Raw data
#
@urlpatterns.route(reports_url + 'data/votes.<format>')
def votes_data(conversation, format):
    filename = conversation.slug + '-votes'
    data = conversation.votes.dataframe()
    return data_response(data, format, filename)


@urlpatterns.route(reports_url + 'data/comments.<format>')
def comments_data(conversation, format):
    filename = conversation.slug + '-comments'
    data = conversation.comments.statistics_summary_dataframe()
    return data_response(data, format, filename)


@urlpatterns.route(reports_url + 'data/users.<format>')
def users_data(conversation, format):
    filename = conversation.slug + '-users'
    data = conversation.users.statistics_summary_dataframe()
    return data_response(data, format, filename)


def data_response(data, format, filename):
    response = HttpResponse(content_type=f'text/{format}')
    filename = f'filename={filename}.{format}'
    response['Content-Disposition'] = f'attachment; {filename}'
    if format == 'json':
        data.to_json(path_or_buf=response, force_ascii=False)
    elif format == 'csv':
        data.to_csv(path_or_buf=response, index=False, mode='a')
    elif format == 'msgpack':
        data.to_msgpack(path_or_buf=response, encoding='utf-8')
    else:
        raise ValueError(f'invalid format: {format}')
    return response
