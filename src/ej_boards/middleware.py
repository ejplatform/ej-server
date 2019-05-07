from django.apps import apps
from django.core.exceptions import MiddlewareNotUsed
from django.urls import resolve


# noinspection PyPep8Naming
def BoardFallbackMiddleware(get_response):  # noqa: N802, C901
    """
    Look for board urls after 404 errors.
    """
    if not apps.is_installed("ej_boards"):
        raise MiddlewareNotUsed

    def middleware(request):
        response = get_response(request)
        if response.status_code != 404:
            return response

        # Match a URL like /<board-slug>/
        slug, _, remaining = request.path[1:].partition("/")
        if remaining:
            return response

        # Handle as /<board-slug>/conversations/
        view, args, kwargs = resolve(f"{slug}/conversations/")
        return view(request, **kwargs)

    return middleware
