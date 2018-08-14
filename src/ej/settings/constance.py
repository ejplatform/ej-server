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
                self.env('ROCKETCHAT_URL', default=''),
                'External RocketChat URL, used for RC IFrame Integration', str
            ),
            'ROCKETCHAT_PRIVATE_URL': (
                self.env('ROCKETCHAT_PRIVATE_URL', default=''),
                'Internal RocketChat URL, used for internal API calls', str
            ),
            'ROCKETCHAT_AUTH_TOKEN': (
                self.env('ROCKETCHAT_AUTH_TOKEN', default=''),
                'RocketChat admin user Token', str
            ),
            'ROCKETCHAT_USER_ID': (
                self.env('ROCKETCHAT_USER_ID', default=''),
                'RocketChat admin user ID', str
            ),
            # Board
            'MAX_BOARD_NUMBER': (
                1,
                'Maximum number of boards of a common user', int
            ),
        }

    CONSTANCE_CONFIG_FIELDSETS = {
        'RocketChat Options': (
            'ROCKETCHAT_URL', 'ROCKETCHAT_PRIVATE_URL',
            'ROCKETCHAT_AUTH_TOKEN', 'ROCKETCHAT_USER_ID'
        ),
    }
