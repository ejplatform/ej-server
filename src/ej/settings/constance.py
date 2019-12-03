from boogie.configurations import Conf, env



class ConstanceConf(Conf):
    """
    This class is responsible for the
    Dynamic django settings, edit on admin page
    https://django-constance.readthedocs.io/en/latest/
    """

    # Constance requires its own backend to work
    CONSTANCE_BACKEND = env("constance.backends.database.DatabaseBackend")
    CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True

    def get_constance_config(self):
        """
        This function return the values that will be used in the admin
        page
        :return: constance_fields
        """
        return {
            "EJ_MAX_BOARD_NUMBER": (
                self.EJ_MAX_BOARD_NUMBER,
                "Maximum number of boards that a common user can create",
                int,
            ),
            "EJ_PROFILE_STATE_CHOICES": (
                self.EJ_PROFILE_STATE_CHOICES,
                "State choices for state field in profile",
                "choicesfield",
            ),
            "EJ_USER_HOME_PATH": (
                self.EJ_USER_HOME_PATH,
                "Landing page for logged user",
                str,
            ),
            "EJ_ANONYMOUS_HOME_PATH": (
                self.EJ_ANONYMOUS_HOME_PATH,
                "Landing page for anonymous user",
                str,
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
        "EJ Options": ("EJ_MAX_BOARD_NUMBER", "EJ_PROFILE_STATE_CHOICES", "EJ_USER_HOME_PATH", "EJ_ANONYMOUS_HOME_PATH")
    }

    # Auxiliary options
    EJ_USER_HOME_PATH = env("/start/", name="{attr}")
    EJ_ANONYMOUS_HOME_PATH = env("/conversations/", name="{attr}")
    EJ_MAX_BOARD_NUMBER = env(1, name="{attr}")
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
