from django.urls import path
from django.views.generic import TemplateView

patterns = []


def route(url, template_name=None, name=None, **kwargs):
    if template_name is not None:
        return route(url, **kwargs)(TemplateView.as_view(template_name=template_name))

    def decorator(func):
        kwargs_ = dict(name=name or func.__name__.replace('_', '-'), **kwargs)
        patterns.append(path(url, func, **kwargs_))
        return func

    return decorator


def get_patterns():
    return list(patterns)
