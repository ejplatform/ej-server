from django.shortcuts import redirect


"""
keep_query_params_after_login_redirect is a middleware to keep query_params after
redirect user to login page. This is useful for process vote choice from ej marketing campaigns,
when user are not logged to EJ.
"""


def _redirect_to_login_with_params(request):
    comment_id = request.GET.get('comment_id')
    choice = request.GET.get('choice')
    query_params = '&comment_id={}&choice={}'.format(comment_id, choice)
    path = request.path
    login_with_params = '/login?next={}{}'.format(path, query_params)
    return redirect(login_with_params)


def KeepQueryParamsAfterLoginRedirect(get_response):
    def middleware(request):
        response = get_response(request)
        if request.GET.get('origin') and request.GET.get('origin') == 'campaign':
            try:
                if request.user.is_authenticated:
                    return response
                else:
                    return _redirect_to_login_with_params(request)
            except Exception as e:
                return _redirect_to_login_with_params(request)
        return response
    return middleware
