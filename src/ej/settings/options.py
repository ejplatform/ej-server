from boogie.configurations import Conf, env

_ = (lambda x: x)


class EjOptions(Conf):
    """
    Options for EJ installation.
    """

    # Integrations with third party services
    EJ_ENABLE_ROCKETCHAT = env(True, name='{attr}')

    # Conversations
    EJ_CONVERSATIONS_ALLOW_PERSONAL_CONVERSATIONS = env(True, name='{attr}')
    EJ_CONVERSATIONS_MAX_COMMENTS = env(2, name='{attr}')

    # Personalization
    EJ_PAGE_TITLE = _('Empurrando Juntos')
    EJ_REGISTER_TEXT = 'Ainda não faz parte do EJ?'
