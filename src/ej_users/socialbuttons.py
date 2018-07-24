from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialApp

from hyperpython.components import fab_link

SOCIAL_BUTTON_REGISTRY = {}


def register_button(provider_id):
    """
    Register a button tag for the given provider
    """

    def decorator(func):
        SOCIAL_BUTTON_REGISTRY[provider_id] = func
        return func

    return decorator


def active_social_apps(request):
    """
    Return a list of active social apps for the current request.
    """
    # Probably we have to filter the valid providers for the current site.
    return SocialApp.objects.values_list('provider', flat=True)


def social_button(provider_id, request):
    """
    Return a social button for the given provider.
    """
    return SOCIAL_BUTTON_REGISTRY[provider_id](request)


def social_buttons(request):
    """
    Return a list of all active social buttons for the current request.
    """
    return [social_button(id, request) for id in active_social_apps(request)]


@register_button('facebook')
def facebook_button(request):
    provider = providers.registry.by_id('facebook', request)
    query = {
        'next': '/start/',
        'method': 'js_sdk',
    }
    url = provider.get_login_url(request, **query)
    return fab_link(url, 'facebook', id='facebook-button')


@register_button('github')
def github_button(request):
    return facebook_button(request)


@register_button('google')
def google_button(request):
    return facebook_button(request)
