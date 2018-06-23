from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.deprecation import MiddlewareMixin

from ej_users.models import User


class UserFallbackMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response  # No need to check for a flatpage for non-404 responses.
        try:
            username = request.path.strip('/')
            owner = get_object_or_404(User, username=username)
            return redirect('user-conversation:list', owner=owner)

        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except Exception:
            if settings.DEBUG:
                raise
            return response
