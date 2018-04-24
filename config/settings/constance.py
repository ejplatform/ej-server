from config.settings.core import env, DEBUG

# Dynamic django settings, edit on admin page
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True
CONSTANCE_CONFIG = {
    # RocketChat integration
    'ROCKETCHAT_URL': (
        env('ROCKETCHAT_URL', default='http://rocketchat:3000'),
        'External RocketChat URL', str),

    'ROCKETCHAT_AUTH_TOKEN': (
        env('ROCKETCHAT_AUTH_TOKEN',
            default=''),
        'RocketChat admin user token', str),

    'ROCKETCHAT_USER_ID': (
        env('ROCKETCHAT_USER_ID', default=''),
        'RocketChat admin user id', str)
}

CONSTANCE_CONFIG_FIELDSETS = {
    'RocketChat Options': (
        'ROCKETCHAT_URL', 'ROCKETCHAT_AUTH_TOKEN', 'ROCKETCHAT_USER_ID'
    ),
}
