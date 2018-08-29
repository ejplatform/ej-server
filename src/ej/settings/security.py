from sidekick import unique as _unique

from boogie.configurations import SecurityConf as Base, env


class SecurityConf(Base):
    INTERNAL_IPS = env([])
    AUTHENTICATION_BACKENDS = [
        'rules.permissions.ObjectPermissionBackend',
        'django.contrib.auth.backends.ModelBackend',
        'allauth.account.auth_backends.AuthenticationBackend',
    ]
    X_FRAME_OPTIONS = env('SAMEORIGIN')
    CORS_ORIGIN_ALLOW_ALL = env(False)
    CORS_ALLOW_CREDENTIALS = env(True)

    def get_cors_origin_whitelist(self, hostname):
        return self.CSRF_TRUSTED_ORIGINS

    def get_csrf_trusted_origins(self, hostname):
        trusted = [
            hostname,
            *(self.env('DJANGO_CSRF_TRUSTED_ORIGINS', type=list) or ()),
        ]
        if self.EJ_ROCKETCHAT_INTEGRATION:
            trusted.append(remove_schema(self.EJ_ROCKETCHAT_URL))
        return unique(trusted)

    def get_allowed_hosts(self, hostname):
        allowed = self.env.list('DJANGO_ALLOWED_HOSTS', default=[]) or []
        return unique([hostname, *allowed])

    def finalize(self, settings):
        settings = super().finalize(settings)

        if self.ENVIRONMENT == 'local':
            settings['INTERNAL_IPS'].append('127.0.0.1')
            settings['CORS_ORIGIN_ALLOW_ALL'] = True
            settings['CSRF_TRUSTED_ORIGINS'].extend(
                'localhost' + x for x in ['', ':8000', ':3000', ':5000']
            )
        return settings


def remove_schema(url):
    _, _, hostname = url.partition('://')
    return hostname


def unique(data):
    return list(_unique(data))
