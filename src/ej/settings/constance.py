from boogie.configurations import Conf, env


class ConstanceConf(Conf):
    """
    Dynamic django settings, edit on admin page
    """

    CONSTANCE_BACKEND = env('constance.backends.database.DatabaseBackend')
    CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True

    def get_constance_config(self):
        return {
            # RocketChat integration
            'ROCKETCHAT_URL': (
                self.ROCKETCHAT_URL,
                'External RocketChat URL, used for RC IFrame Integration', 'charfield'
            ),
            'ROCKETCHAT_PRIVATE_URL': (
                self.ROCKETCHAT_PRIVATE_URL,
                'Internal RocketChat URL, used for internal API calls', 'charfield'
            ),
            'ROCKETCHAT_AUTH_TOKEN': (
                self.ROCKETCHAT_AUTH_TOKEN,
                'RocketChat admin user Token', 'charfield'
            ),
            'ROCKETCHAT_USER_ID': (
                self.ROCKETCHAT_USER_ID,
                'RocketChat admin user ID', 'charfield'
            ),
            # EJ Options
            'EJ_MAX_BOARD_NUMBER': (
                self.EJ_MAX_BOARD_NUMBER,
                'Maximum number of boards that a common user can create', int
            ),
        }

    CONSTANCE_CONFIG_FIELDSETS = {
        'RocketChat Options': (
            'ROCKETCHAT_URL', 'ROCKETCHAT_PRIVATE_URL',
            'ROCKETCHAT_AUTH_TOKEN', 'ROCKETCHAT_USER_ID',
        ),
        'EJ Options': (
            'EJ_MAX_BOARD_NUMBER',
        )
    }
    CONSTANCE_ADDITIONAL_FIELDS = {
        'charfield': ['django.forms.fields.CharField', {
            'widget': 'django.forms.TextInput'
        }]
    }

    # Auxiliary options
    EJ_MAX_BOARD_NUMBER = env(1, name='{attr}')

    def get_rocketchat_url(self, hostname):
        default = f'talks.{hostname}'
        return self.env('ROCKETCHAT_URL', default=default)

    def get_rocketchat_private_url(self, rocketchat_url):
        return self.env('ROCKETCHAT_PRIVATE_URL', default=rocketchat_url)

    ROCKETCHAT_USER_ID = env('admin', name='{attr}')
    ROCKETCHAT_AUTH_TOKEN = env('', name='{attr}')
