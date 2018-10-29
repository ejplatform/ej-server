from django.conf import settings
from django.http import Http404
from django.urls import resolve
from django.utils.text import slugify

from ej_conversations.models import Conversation


def ConversationFallbackMiddleware(get_response):  # noqa: N802
    """
    Look for conversations urls after 404 errors.
    """

    def middleware(request):
        response = get_response(request)
        if response.status_code != 404:
            return response

        # noinspection PyBroadException
        try:
            slugfied_terms = [slugify(x) for x in request.path.split('/')]
            new_path = '/'.join(slugfied_terms)

            view, args, kwargs = resolve(new_path)
            new_response = view(request, **kwargs)

            return new_response

        except Http404:
            return response
        except Conversation.DoesNotExist:
            return response
        except Exception:
            if settings.DEBUG:
                raise
            return response

    return middleware
