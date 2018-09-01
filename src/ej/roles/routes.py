from django.db.models import Model
from django.http import Http404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from boogie.router import Router
from hyperpython import render, a, span, div, h1
from hyperpython.components import html_list, html_map
from .utils import register_queryset

urlpatterns = Router(
    template='generic.jinja2',
)


@urlpatterns.route('')
def role_index():
    data = []
    classes = set()

    # Collect all models and roles in the default render registry
    for (cls, _) in render.registry:
        if not issubclass(cls, Model) or cls in classes:
            continue
        classes.add(cls)
        name = cls.__name__
        href = reverse('role-model', kwargs={'model': name.lower()})
        data.append((name, span([a(name, href=href), ': ' + cls.__doc__])))

    # Now we collect the queryset renderers
    classes = set()
    for (cls, _) in register_queryset.registry:
        classes.add(cls)
        name = cls.__name__
        href = reverse('role-model-queryset', kwargs={'model': name.lower()})
        data.append([
            name + ' (queryset)',
            span([a(name, href=href), ': ' + cls.__doc__]),
        ])

    return {'data': html_map(data)}


@urlpatterns.route('<model>')
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


@urlpatterns.route('<model>/<role>/')
def role_model_list(request, model, role):
    cls = get_class(model)
    kwargs = query_to_kwargs(request)
    size = kwargs.pop('size', 10)
    data = []
    for idx, obj in enumerate(cls.objects.all()[:size], 1):
        link = reverse('role-model-instance',
                       kwargs={'model': model, 'role': role, 'id': obj.id})
        key = span([f'{idx}) ', a(str(obj), href=link)])
        data.append((key, render(obj, role, **kwargs)))

    return {'data': html_map(data)}


@urlpatterns.route('<model>/<role>/<int:id>/')
def role_model_instance(request, model, role, id):
    cls = get_class(model)
    obj = cls.objects.get(id=id)
    kwargs = query_to_kwargs(request)
    return {'data': render(obj, role, **kwargs)}


@urlpatterns.route('qs/<model>/<role>/')
def role_queryset(request, model, role):
    cls = get_class(model)
    qs = cls.objects.all()
    kwargs = query_to_kwargs(request)
    size = kwargs.pop('size', 10)
    return {'data': render(qs[:size], role, **kwargs)}


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
    for (cls, _) in render.registry:
        if cls.__name__.lower() == model:
            return cls
    raise Http404


def get_roles(cls):
    """
    Return a list of roles assigned to the given class.
    """
    roles = []
    for (cls_, role) in render.registry:
        if cls_ is cls and role is not None:
            roles.append(role)
    if roles:
        return roles
    else:
        raise Http404
