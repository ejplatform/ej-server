from pprint import pformat

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.flatpages.models import FlatPage
from django.db.models import Model
from django.http import Http404
from django.urls import reverse
from django.utils.translation import ugettext as _
from hyperpython import html, span, a, div, h1
from hyperpython.components import html_list, html_map

from boogie.router import Router
from ej.roles.utils import register_queryset
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


def role_index():
    data = []
    classes = set()

    # Collect all models and roles in the default render registry
    for (cls, __) in html.registry:
        if not issubclass(cls, Model) or cls in classes:
            continue
        classes.add(cls)
        name = cls.__name__
        href = reverse('role-model', kwargs={'model': name.lower()})
        data.append((name, span([a(name, href=href), ': ' + get_doc(cls)])))

    # Now we collect the queryset renderers
    classes = set()
    for (cls, __) in register_queryset.registry:
        classes.add(cls)
        name = cls.__name__
        href = reverse('role-model-queryset', kwargs={'model': name.lower()})
        data.append([
            name + ' (queryset)',
            span([a(name, href=href), ': ' + get_doc(cls)]),
        ])

    return {'model_roles': data}


def role_model(model):
    links = []
    cls = get_class(model)
    for role in get_roles(cls):
        href = reverse('role-model-list',
                       kwargs={'model': model, 'role': role})
        links.append(a(role, href=href))

    if not links:
        raise Http404
    else:
        return {'data': div([h1(_('List of roles')), html_list(links)])}


def role_model_list(request, model, role):
    cls = get_class(model)
    kwargs = query_to_kwargs(request)
    size = kwargs.pop('size', 10)
    data = []
    for idx, obj in enumerate(cls.objects.all()[:size], 1):
        link = reverse('role-model-instance',
                       kwargs={'model': model, 'role': role, 'id': obj.id})
        key = span([f'{idx}) ', a(str(obj), href=link)])
        data.append((key, html(obj, role, **kwargs)))

    return {'data': html_map(data)}


def role_model_instance(request, model, role, id):
    cls = get_class(model)
    obj = cls.objects.get(id=id)
    kwargs = query_to_kwargs(request)
    return {'data': html(obj, role, **kwargs)}


def role_queryset(request, model, role):
    cls = get_class(model)
    qs = cls.objects.all()
    kwargs = query_to_kwargs(request)
    size = kwargs.pop('size', 10)
    return {'data': html(qs[:size], role, **kwargs)}


#
# Utility functions
#
def query_to_kwargs(request):
    """
    Read extra arguments from url to pass to object renderers.
    """

    def convert(x):
        for func in [int, float, complex]:
            try:
                return func(x)
            except ValueError:
                pass
        return x

    base = {k: convert(v[0]) for k, v in dict(request.GET)}
    base.setdefault('request', request)
    return base


def get_class(model):
    """
    Return class for string reference of model.
    """
    for (cls, __) in html.registry:
        if cls.__name__.lower() == model:
            return cls
    raise Http404


def get_roles(cls):
    """
    Return a list of roles assigned to the given class.
    """
    roles = []
    for (cls_, role) in html.registry:
        if cls_ is cls and role is not None:
            roles.append(role)
    if roles:
        return roles
    else:
        raise Http404


def get_doc(x):
    """
    Return the docstring for the given object.
    """
    try:
        return x.__doc__ or ''
    except AttributeError:
        return type(x).__doc__ or ''
