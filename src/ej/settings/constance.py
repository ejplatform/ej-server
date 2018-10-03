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
                'State choices for state field in profile', 'choicesfield'
            ),
        }

    CONSTANCE_ADDITIONAL_FIELDS = {
        'charfield': ['django.forms.fields.CharField', {
            'widget': 'django.forms.TextInput',
            'required': False,
        }],
        'choicesfield': ['django.forms.ChoiceField', {
            'required': False,
        }]
    }

    CONSTANCE_CONFIG_FIELDSETS = {
        'EJ Options': (
            'EJ_MAX_BOARD_NUMBER',
            'EJ_STATE_MAX_LENGTH',
            'EJ_STATE_CHOICES',
        )
    }

    # Auxiliary options
    EJ_MAX_BOARD_NUMBER = env(1, name='{attr}')
    EJ_STATE_MAX_LENGTH = env(2, name='{attr}')
    EJ_STATE_CHOICES = env(
        (('AC', 'Acre'),
            ('AL', 'Alagoas'),
            ('AP', 'Amapá'),
            ('AM', 'Amazonas'),
            ('BA', 'Bahia'),
            ('CE', 'Ceará'),
            ('DF', 'Distrito Federal'),
            ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'),
            ('MA', 'Maranhão'),
            ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'),
            ('PA', 'Pará'),
            ('PB', 'Paraíba'),
            ('PR', 'Paraná'),
            ('PE', 'Pernambuco'),
            ('PI', 'Piauí'),
            ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondônia'),
            ('RR', 'Roraima'),
            ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'),
            ('SE', 'Sergipe'),
            ('TO', 'Tocantins'),),
        name='{attr}'
    )
