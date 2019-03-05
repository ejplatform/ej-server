import json

from django.contrib.auth import get_user_model
from django.http import HttpResponse

from boogie.router import Router
from ej_conversations.models import Conversation
from ej_conversations.routes import conversation_url, check_promoted

urlpatterns = Router(
    template=['ej_reports/{name}.jinja2', 'generic.jinja2'],
    models={'conversation': Conversation},
    login=True,
    perms=['ej.can_view_report_detail:conversation']
)
app_name = 'ej_reports'
reports_url = conversation_url + 'reports/'
loose_perms = []
strict_perms = urlpatterns.perms
User = get_user_model()


#
# Base report URLs
#
@urlpatterns.route(reports_url, perms=loose_perms)
def index(request, conversation, slug, check=check_promoted):
    check(conversation)
    user = request.user
    can_view_detail = user.has_perm('ej.can_view_report_detail', conversation)
    statistics = conversation.statistics()

    # Force clusterization, when possible
    clusterization = conversation.get_clusterization(None)
    if clusterization:
        clusterization.update_clusterization()
        clusters = clusterization.clusters.all()
    else:
        clusters = ()

    return {
        'clusters': clusters,
        'conversation': conversation,
        'statistics': statistics,
        'can_view_detail': can_view_detail,
    }


@urlpatterns.route(reports_url + 'participants/')
def participants_table(conversation, slug, check=check_promoted):
    return {'conversation': check(conversation)}


@urlpatterns.route(reports_url + 'scatter/', perms=loose_perms)
def scatter(conversation, slug, check=check_promoted):
    return {'conversation': check(conversation)}


@urlpatterns.route(reports_url + 'scatter/pca.json', perms=loose_perms)
def scatter_pca_json(conversation, slug, check=check_promoted):
    check(conversation)
    df = conversation.votes.pca_reduction()
    return {'votes': json.dumps(df.tolist())}


#
# Raw data
#
@urlpatterns.route(reports_url + 'data/votes.<format>')
def votes_data(conversation, format, slug, check=check_promoted):
    check(conversation)
    filename = conversation.slug + '-votes'
    data = conversation.votes.dataframe()
    return data_response(data, format, filename)


@urlpatterns.route(reports_url + 'data/comments.<format>')
def comments_data(conversation, format, slug, check=check_promoted):
    check(conversation)
    check(conversation)
    filename = conversation.slug + '-comments'
    data = conversation.comments.statistics_summary_dataframe()
    return data_response(data, format, filename)


@urlpatterns.route(reports_url + 'data/users.<format>')
def users_data(conversation, format, slug, check=check_promoted):
    check(conversation)
    filename = conversation.slug + '-users'
    data = conversation.users.statistics_summary_dataframe()
    return data_response(data, format, filename)


#
# Auxiliary functions
#
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


#
# Introspection
#
loose_perms_views = [index, scatter, scatter_pca_json]
strict_perms_views = [participants_table, votes_data, comments_data, users_data]
