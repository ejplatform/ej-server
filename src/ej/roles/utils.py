from types import MappingProxyType

from django.db import models
from django.db.models import QuerySet
from hyperpython import html, Blob
from hyperpython.components import html_list
from hyperpython.html import django_loader


def with_template(model, role, template=None, queryset=False):
    """
    Decorator Register element rendered from a template.

    Args:
        model (type):
            Python class or Django model that should be used to render the
            template.
        role (str):
            The name of the role associated with the view function.
        template (str):
            Name of the template used to render the model.
        queryset (bool):
            If true, register renderer to a queryset instead of a model object.
    """
    if isinstance(model, (list, tuple)):
        *models, model = list(model)
    else:
        models = []

    def decorator(func):
        nonlocal template

        if template is None:
            template = f"ej/role/{func.__name__.replace('_', '-')}.jinja2"

        if queryset:
            renderer = render_with_template(func, template)
            for other in models:
                html.register_queryset(other, role)(renderer)
            return html.register_queryset(model, role)(renderer)
        else:
            for other in models:
                html.register_template(other, template, role=role)(func)
            return html.register_template(model, template, role=role)(func)

    return decorator


def queryset_closure():
    """
    Register function that handle rendering of querysets.
    """
    registry = {}

    def render_queryset(qs, role=None, **kwargs):
        """
        Renders a queryset object. Dispatch by role and model.
        """
        model = qs.model
        key = (model, role)
        if role:
            kwargs["role"] = role

        try:
            renderer = registry[key]
        except KeyError:
            return html_list(html(x, **kwargs) for x in qs)
        else:
            return renderer(qs, **kwargs)

    def register(model, role=None):
        """
        Decorator that register queryset renderer for the given model and role.
        """

        if not (isinstance(model, type) and issubclass(model, models.Model)):
            raise TypeError("model must be a Django Model subclass")

        def decorator(func):
            registry[model, role] = func
            return func

        return decorator

    render_queryset.registry = MappingProxyType(registry)
    render_queryset.register = register
    return render_queryset


def render_with_template(func, template):
    """
    Return a render function that renders using a template.

    Args:
        func:
            Function that computes the context dictionary passed to template.
        template:
            Name (or list of names) of the template.
    """
    template = django_loader.get_template(template)
    renderer = template.render

    def wrapped(obj, **kwargs):
        context = func(obj, **kwargs)
        request = context.get("request")
        data = renderer(context=context, request=request)
        return Blob(data)

    return wrapped


register_queryset = queryset_closure()
html.register(QuerySet)(register_queryset)
html.with_template = with_template
html.register_queryset = register_queryset.register
