from .decorators import with_headers


def ContentSecurityPolicyMiddleware(get_response):  # noqa: N802
    """
    Apply Content-Security-Policy headers in all pages.
    """

    def middleware(request):
        return with_headers(get_response(request))

    return middleware
