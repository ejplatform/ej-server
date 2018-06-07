from django.conf import settings
from ej_users.routes import user_conversations
from django.http import Http404
from ej_users.models import User

from django.utils.deprecation import MiddlewareMixin


class UserFallbackMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response  # No need to check for a flatpage for non-404 responses.
        try:
            # request.path = /username/
            username = request.path.split('/')[1]
            user = User.objects.get(username=username)
            return user_conversations(request, user)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except Exception:
            if settings.DEBUG:
                raise
            return response
