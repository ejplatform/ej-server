from boogie.configurations import Conf, env

_ = (lambda x: x)


class EjOptions(Conf):
    """
    Options for EJ installation.
    """

    # Integrations with third party services
    EJ_ROCKETCHAT_INTEGRATION = env(False, name='{attr}')

    # Conversations
    EJ_CONVERSATIONS_ALLOW_PERSONAL_CONVERSATIONS = env(True, name='{attr}')
    EJ_CONVERSATIONS_MAX_COMMENTS = env(2, name='{attr}')

    # TODO: remove those in the future? Maybe all personalization strings
    # should be options in Django constance with a cache fallback
    # Personalization
    EJ_ANONYMOUS_HOME_PATH = env('/home/', name='{attr}')
    EJ_USER_HOME_PATH = env('/conversations/', name='{attr}')
    EJ_PAGE_TITLE = env(_('EJ Platform'), name='{attr}')
    EJ_REGISTER_TEXT = 'Ainda não faz parte do EJ?'

    # Allow instances to exclude some profile fields from visualization
    EJ_EXCLUDE_PROFILE_FIELDS = env([], name='{attr}')
