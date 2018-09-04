from .decorators import with_headers


def ContentSecurityPolicyMiddleware(get_response):
    """
    Apply Content-Security-Policy headers in all pages.
    """

    def middleware(request):
        return with_headers(get_response(request))

    return middleware
