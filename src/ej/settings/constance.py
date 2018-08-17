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
                'External RocketChat URL, used for RC IFrame Integration', str
            ),
            'ROCKETCHAT_PRIVATE_URL': (
                self.ROCKETCHAT_PRIVATE_URL,
                'Internal RocketChat URL, used for internal API calls', str
            ),
            'ROCKETCHAT_AUTH_TOKEN': (
                self.ROCKETCHAT_AUTH_TOKEN,
                'RocketChat admin user Token', str
            ),
            'ROCKETCHAT_USER_ID': (
                self.ROCKETCHAT_USER_ID,
                'RocketChat admin user ID', str
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

    # Auxiliary options
    EJ_MAX_BOARD_NUMBER = env(1, name='{attr}')

    ROCKETCHAT_URL = env('', name='{attr}')
    ROCKETCHAT_PRIVATE_URL = env('', name='{attr}')
    ROCKETCHAT_AUTH_TOKEN = env('', name='{attr}')
    ROCKETCHAT_USER_ID = env('', name='{attr}')
