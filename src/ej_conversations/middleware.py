from django.conf import settings
from django.utils.text import slugify

from ej_conversations.models import Conversation


def ConversationFallbackMiddleware(get_response):  # noqa: N802
    """
    Look for conversations urls after 404 errors.
    """
    from .routes import detail
    view_function = detail.as_view()

    def middleware(request):
        response = get_response(request)
        if response.status_code != 404:
            return response

        # noinspection PyBroadException
        try:
            slugfied_terms = [slugify(x) for x in request.path.split('/')]
            slug = slugfied_terms[2]

            conversation = Conversation.objects.get(slug=slug)
            return view_function(request, conversation=conversation)

        except Conversation.DoesNotExist:
            return response
        except Exception:
            if settings.DEBUG:
                raise
            return response

    return middleware
