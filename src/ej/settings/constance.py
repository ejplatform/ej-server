from boogie.configurations import Conf, env


class ConstanceConf(Conf):
    """
    Dynamic django settings, edit on admin page
    """

    CONSTANCE_BACKEND = env("constance.backends.database.DatabaseBackend")
    CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True

    def get_constance_config(self):
        return {
            "EJ_MAX_BOARD_NUMBER": (
                self.EJ_MAX_BOARD_NUMBER,
                "Maximum number of boards that a common user can create",
                int,
            ),
            "EJ_LISTEN_TO_COMMUNITY_SIGNATURE_CONVERSATIONS_LIMIT": (
                self.EJ_LISTEN_TO_COMMUNITY_SIGNATURE_CONVERSATIONS_LIMIT,
                "Maximum number of conversations that a common user can create if they have Listen to Community signature.",
                int,
            ),
            "EJ_LISTEN_TO_COMMUNITY_SIGNATURE_VOTE_LIMIT": (
                self.EJ_LISTEN_TO_COMMUNITY_SIGNATURE_VOTE_LIMIT,
                "Maximum number of votes that a common user can give if they have Listen to Community signature.",
                int,
            ),
            "EJ_LISTEN_TO_CITY_SIGNATURE_CONVERSATIONS_LIMIT": (
                self.EJ_LISTEN_TO_CITY_SIGNATURE_CONVERSATIONS_LIMIT,
                "Maximum number of conversations that a common user can create if they have Listen to City signature.",
                int,
            ),
            "EJ_LISTEN_TO_CITY_SIGNATURE_VOTE_LIMIT": (
                self.EJ_LISTEN_TO_CITY_SIGNATURE_VOTE_LIMIT,
                "Maximum number of votes that a common user can give if they have Listen to City signature.",
                int,
            ),
            "EJ_PROFILE_STATE_CHOICES": (
                self.EJ_PROFILE_STATE_CHOICES,
                "State choices for state field in profile",
                "choicesfield",
            ),
            "EJ_LANDING_PAGE_DOMAIN": (
                self.EJ_LANDING_PAGE_DOMAIN,
                "Redirect url for when the user is not logged in to the platform",
                "charfield",
            ),
        }

    CONSTANCE_ADDITIONAL_FIELDS = {
        "charfield": [
            "django.forms.fields.CharField",
            {"widget": "django.forms.TextInput", "required": False},
        ],
        "choicesfield": ["django.forms.ChoiceField", {"required": False}],
    }

    CONSTANCE_CONFIG_FIELDSETS = {
        "EJ Options": (
            "EJ_MAX_BOARD_NUMBER",
            "EJ_LISTEN_TO_COMMUNITY_SIGNATURE_CONVERSATIONS_LIMIT",
            "EJ_LISTEN_TO_COMMUNITY_SIGNATURE_VOTE_LIMIT",
            "EJ_LISTEN_TO_CITY_SIGNATURE_CONVERSATIONS_LIMIT",
            "EJ_LISTEN_TO_CITY_SIGNATURE_VOTE_LIMIT",
            "EJ_PROFILE_STATE_CHOICES",
            "EJ_LANDING_PAGE_DOMAIN",
        )
    }

    # Auxiliary options
    EJ_MAX_BOARD_NUMBER = env(1, name="{attr}")
    EJ_LISTEN_TO_COMMUNITY_SIGNATURE_CONVERSATIONS_LIMIT = env(20, name="{attr}")
    EJ_LISTEN_TO_COMMUNITY_SIGNATURE_VOTE_LIMIT = env(100000, name="{attr}")
    EJ_LISTEN_TO_CITY_SIGNATURE_CONVERSATIONS_LIMIT = env(21, name="{attr}")
    EJ_LISTEN_TO_CITY_SIGNATURE_VOTE_LIMIT = env(100000, name="{attr}")
    EJ_PROFILE_STATE_CHOICES = env(
        (
            ("AC", "Acre"),
            ("AL", "Alagoas"),
            ("AP", "Amapá"),
            ("AM", "Amazonas"),
            ("BA", "Bahia"),
            ("CE", "Ceará"),
            ("DF", "Distrito Federal"),
            ("ES", "Espírito Santo"),
            ("GO", "Goiás"),
            ("MA", "Maranhão"),
            ("MT", "Mato Grosso"),
            ("MS", "Mato Grosso do Sul"),
            ("MG", "Minas Gerais"),
            ("PA", "Pará"),
            ("PB", "Paraíba"),
            ("PR", "Paraná"),
            ("PE", "Pernambuco"),
            ("PI", "Piauí"),
            ("RJ", "Rio de Janeiro"),
            ("RN", "Rio Grande do Norte"),
            ("RS", "Rio Grande do Sul"),
            ("RO", "Rondônia"),
            ("RR", "Roraima"),
            ("SC", "Santa Catarina"),
            ("SP", "São Paulo"),
            ("SE", "Sergipe"),
            ("TO", "Tocantins"),
        ),
        name="{attr}",
    )
    EJ_LANDING_PAGE_DOMAIN = env("/login", name="{attr}")
