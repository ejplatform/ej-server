from boogie.configurations import Conf, env

_ = lambda x: x


class EjOptions(Conf):
    """
    Options for EJ installation.
    """

    # Conversations and boards limits
    EJ_MAX_COMMENTS_PER_CONVERSATION = env(2, name="{attr}")
    EJ_MAX_CONVERSATIONS_PER_BOARD = env(None, type=int, name="{attr}")
    EJ_ENABLE_BOARDS = env(True, name="{attr}")

    # Disable parts of the system
    EJ_ENABLE_PROFILES = env(True, name="{attr}")
    EJ_ENABLE_NOTIFICATIONS = env(True, name="{attr}")
    EJ_ENABLE_CLUSTERS = env(True, name="{attr}")
    EJ_ENABLE_DATAVIZ = env(True, name="{attr}")
    EJ_ENABLE_GAMIFICATION = env(True, name="{attr}")

    # Allow instances to exclude some profile fields from visualization
    EJ_PROFILE_EXCLUDE_FIELDS = env([], name="{attr}")

    # Messages
    EJ_PAGE_TITLE = env(_("EJ Platform"), name="{attr}")
    EJ_REGISTER_TEXT = _("Not part of EJ yet?")
    EJ_LOGIN_TITLE_TEXT = _("Welcome!")

    # Integrations with Rocket.Chat
    EJ_ROCKETCHAT_INTEGRATION = env(False, name="{attr}")
    EJ_ROCKETCHAT_INTERNAL_DOMAINS = env("", name="{attr}")
    EJ_ROCKETCHAT_URL = env("http://localhost:3000", name="{attr}")
    EJ_ROCKETCHAT_API_URL = env("", name="{attr}")
    EJ_ROCKETCHAT_AUTH_TOKEN = env("", name="{attr}")
    EJ_ROCKETCHAT_ADMIN_USERNAME = env("", name="{attr}")
    EJ_ROCKETCHAT_ADMIN_ID = env("", name="{attr}")
    EJ_ROCKETCHAT_ADMIN_PASSWORD = env("", name="{attr}")
