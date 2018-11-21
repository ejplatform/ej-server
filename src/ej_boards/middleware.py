from django.conf import settings
from django.utils.text import slugify
from django.urls import resolve
from django.http import Http404, HttpResponsePermanentRedirect

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
            slugfied_terms = [slugify(x) for x in request.path.split('/')]
            slug = slugfied_terms[1]

            if '/' in slug:
                return response

            board = Board.objects.get(slug=slug)

            # make a url with the real board slug e.g.: /Slug/edit/ becomes /slug/edit/
            new_path = '/'.join(slugfied_terms)

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

def BoardDomainRedirectMiddleware(get_response):

  from ej_boards.models import Board

  def middleware(request):
    response = get_response(request)
    path_info = request.META['PATH_INFO']
    if(path_info == '/home/'):
      domain = request.META['HTTP_HOST'].split(':')[0]
      board, board_exists = Board.with_custom_domain(domain)
      if(board_exists):
        return HttpResponsePermanentRedirect('/%s/conversations' % board)
    return response

  return middleware
