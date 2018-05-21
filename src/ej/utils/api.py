import importlib

from django.core.exceptions import ImproperlyConfigured


def register_module(router, path):
    """
    Import routes from a module in the given path. The module must define
    a register() function that receives a router and an optional base path
    and register the corresponding endpoints in it.

    Usage:
        .. code-block:: python

            # in project's urls.py
            register_module(router_v1, 'my_app.api')


            # in my_mapp/api.py

            def register(router):
                router.register(r'^users/', UsersViewSet)
                ...
    """

    module = importlib.import_module(path)

    try:
        register = module.register
    except AttributeError:
        raise ImproperlyConfigured(
            f'The api module {path} must define a register(route) function that '
            'receives a router as a single argument.'
        )
    else:
        register(router)
