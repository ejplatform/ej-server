from django.conf import settings
from django.utils.text import slugify
from django.urls import resolve
from django.http import Http404

from .models import Board


def BoardFallbackMiddleware(get_response):  # noqa: N802, C901
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
            slug = slugify(request.path.split('/')[1])

            if '/' in slug:
                return response

            board = Board.objects.get(slug=slug)

            # make a url with the real board slug e.g.: /Slug/edit/ becomes /slug/edit/
            new_path = board.get_absolute_url() + '/'.join(request.path.split('/')[2:])

            try:
                view, args, kwargs = resolve(new_path)
                new_response = view(request, **kwargs)
                return new_response
            except Http404:
                # accessing /board-slug/
                if '/' not in request.path.strip('/'):
                    return view_function(request, board=board)

                return response

        except Board.DoesNotExist:
            return response
        except Exception:
            if settings.DEBUG:
                raise
            return response

    return middleware
