from django.conf import settings

from .models import Board


def BoardFallbackMiddleware(get_response):  # noqa: N802
    """
    Look for board urls after 404 errors.
    """
    from .routes import conversation_list
    view_function = conversation_list.as_view()

    def middleware(request):
        response = get_response(request)
        if response.status_code != 404:
            return response

        # noinspection PyBroadException
        try:
            slug = request.path.strip('/')
            if '/' in slug:
                return response
            board = Board.objects.get(slug=slug)
            return view_function(request, board=board)
        except Board.DoesNotExist:
            return response
        except Exception:
            if settings.DEBUG:
                raise
            return response

    return middleware
