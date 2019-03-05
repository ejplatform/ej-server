from pprint import pformat

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext as _

from boogie.router import Router
from ej_configurations.utils import flat_pages_route, superuser_required
from ej_conversations.models import Conversation, Comment, Vote

app_name = 'ej_configurations'
urlpatterns = Router(
    template='configurations/{name}.jinja2',
    decorators=[superuser_required],
)
loose_perms = {'decorators': ()}


#
# Administrative views: information and introspection about application state
#
@urlpatterns.route('')
def index():
    return {}


@urlpatterns.route('django-settings/')
def django_settings(request):
    if not request.user.is_superuser:
        raise PermissionError
    data = [(name, pformat(getattr(settings, name)))
            for name in dir(settings) if name.isupper()]
    return {'settings': sorted(data)}


@urlpatterns.route('info/')
def info():
    count = (lambda x: x.objects.count())
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


@urlpatterns.route('styles/')
def styles():
    return {}


@urlpatterns.route('fragment/')
def fragment_list():
    return {}


#
# Public views
#
@urlpatterns.route('fragment/<name>/', **loose_perms)
def fragment_error(name):
    return {'name': name}


@urlpatterns.route('social/', **loose_perms)
def social():
    from ej_configurations import social_icons
    return {'icons': social_icons()}


urlpatterns.register(flat_pages_route('rules'), 'rules/', **loose_perms)
urlpatterns.register(flat_pages_route('faq'), 'faq/', **loose_perms)
urlpatterns.register(flat_pages_route('about-us'), 'about-us/', **loose_perms)
urlpatterns.register(flat_pages_route('usage'), 'usage/', **loose_perms)
