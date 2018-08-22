from boogie.configurations import Conf, env


class ConstanceConf(Conf):
    """
    Dynamic django settings, edit on admin page
    """

    CONSTANCE_BACKEND = env('constance.backends.database.DatabaseBackend')
    CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True

    def get_constance_config(self):
        return {
            'EJ_MAX_BOARD_NUMBER': (
                self.EJ_MAX_BOARD_NUMBER,
                'Maximum number of boards that a common user can create', int
            ),
        }

    CONSTANCE_CONFIG_FIELDSETS = {
        'EJ Options': (
            'EJ_MAX_BOARD_NUMBER',
        )
    }
    CONSTANCE_ADDITIONAL_FIELDS = {
        'charfield': ['django.forms.fields.CharField', {
            'widget': 'django.forms.TextInput',
            'required': False,
        }]
    }

    # Auxiliary options
    EJ_MAX_BOARD_NUMBER = env(1, name='{attr}')
