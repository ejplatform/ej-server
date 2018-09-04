from boogie.configurations import Conf, env

_ = (lambda x: x)


class EjOptions(Conf):
    """
    Options for EJ installation.
    """

    # Integrations with Rocket.Chat
    EJ_ROCKETCHAT_INTEGRATION = env(False, name='{attr}')
    EJ_ROCKETCHAT_URL = env('http://localhost:3000', name='{attr}')
    EJ_ROCKETCHAT_AUTH_TOKEN = env('', name='{attr}')
    EJ_ROCKETCHAT_USERNAME = env('ej-admin', name='{attr}')
    EJ_ROCKETCHAT_USER_ID = env('', name='{attr}')

    # Conversations Configurations
    EJ_CONVERSATIONS_ALLOW_PERSONAL_CONVERSATIONS = env(True, name='{attr}')
    EJ_CONVERSATIONS_MAX_COMMENTS = env(2, name='{attr}')

    # TODO: remove those in the future? Maybe all personalization strings
    # should be options in Django constance with a cache fallback
    # Personalization
    EJ_ANONYMOUS_HOME_PATH = env('/home/', name='{attr}')
    EJ_USER_HOME_PATH = env('/conversations/', name='{attr}')

    # Allow instances to exclude some profile fields from visualization
    EJ_EXCLUDE_PROFILE_FIELDS = env([], name='{attr}')

    # Messages
    EJ_PAGE_TITLE = env(_('EJ Platform'), name='{attr}')
    EJ_REGISTER_TEXT = _('Not part of EJ yet?')
    EJ_LOGIN_TITLE_TEXT = _('Login in EJ')
