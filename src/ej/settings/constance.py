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
            'EJ_STATE_MAX_LENGTH': (
                self.EJ_STATE_MAX_LENGTH,
                'Max length for state field in profile', int
            ),
            'EJ_STATE_CHOICES': (
                self.EJ_STATE_CHOICES,
                'State choices for state field in profile', tuple
            ),
        }

    CONSTANCE_CONFIG_FIELDSETS = {
        'EJ Options': (
            'EJ_MAX_BOARD_NUMBER',
            'EJ_STATE_MAX_LENGTH'
            'EJ_STATE_CHOICES',
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
    EJ_STATE_MAX_LENGTH = env(2, name='{attr}')
    EJ_STATE_CHOICES = env(
        (('ST', 'State'),('PV', 'Province'),),
        name='{attr}'
    )