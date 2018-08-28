from pprint import pformat

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext as _

from boogie.router import Router
from ej_conversations.models import Conversation, Comment, Vote

app_name = 'ej_configurations'
urlpatterns = Router(
    template='configurations/{name}.jinja2',
)


@urlpatterns.route('', staff=True)
def index(request):
    return {}


@urlpatterns.route('info/', staff=True)
def info():
    return {
        # Generic info
        'user_count': count(get_user_model()),
        'flatpages': FlatPage.objects.values_list('url'),

        # Conversations
        'conversations_counts': {
            _('Conversations'): count(Conversation),
            _('Votes'): count(Vote),
            _('Comments'): count(Comment),
        }
    }


@urlpatterns.route('fragment/', staff=True)
def fragment_list():
    return {}


@urlpatterns.route('fragment/<name>/')
def fragment_error(request, name):
    return {
        'name': name,
    }


@urlpatterns.route('styles/')
def styles():
    return {}


@urlpatterns.route('django-settings/')
def django_settings(request):
    if not request.user.is_superuser:
        raise PermissionError
    data = [(name, pformat(getattr(settings, name)))
            for name in dir(settings) if name.isupper()]
    return {'settings': sorted(data)}


#
# Utility functions
#
def count(model):
    return model.objects.count()


