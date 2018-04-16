from config.settings.core import env, DEBUG

# Dynamic django settings, edit on admin page
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True
CONSTANCE_CONFIG = {
    # RocketChat integration
    'MONGO_URL': (
        env('ROCKETCHAT_MONGO_URL', default='mongodb://mongo:27017'),
        'Internal RocketChat database URL', str),

    'ROCKETCHAT_URL': (
        env('ROCKETCHAT_URL', default='http://rocketchat:3000'),
        'External RocketChat URL', str),

    'ROCKETCHAT_AUTH_TOKEN': (
        env('ROCKETCHAT_AUTH_TOKEN',
            default='yItGp9o3XbkUwBHPo80R-3tCXnZhHaUZnKK3Ix6XoD9'),
        'RocketChat admin user token', str),

    'ROCKETCHAT_USER_ID': (
        env('ROCKETCHAT_USER_ID', default='62bfHvpYqLoa7we7B'),
        'RocketChat admin user id', str)
}

CONSTANCE_CONFIG_FIELDSETS = {
    'RocketChat Options': (
        'MONGO_URL', 'ROCKETCHAT_URL',
        'ROCKETCHAT_AUTH_TOKEN', 'ROCKETCHAT_USER_ID'),
}

X_FRAME_OPTIONS = f'ALLOW-FROM http://localhost:3000'
