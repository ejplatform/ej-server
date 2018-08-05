from boogie.configurations import SecurityConf as Base, env


class SecurityConf(Base):
    INTERNAL_IPS = env([])

    X_FRAME_OPTIONS = 'DENY'

    CORS_ORIGIN_ALLOW_ALL = False
    CORS_ALLOW_CREDENTIALS = True
    CORS_ORIGIN_REGEX_WHITELIST = (r'^(https?://)?[\w.]*ejplatform\.org$',)

    CSRF_TRUSTED_ORIGINS = [
        'ejplatform.org',
        'talks.ejplatform.org'
        'dev.ejplatform.org',
        'talks.dev.ejplatform.org',
    ]

    def finalize(self, settings):
        if self.ENVIRONMENT == 'local':
            del settings['X_FRAME_OPTIONS']
            settings['INTERNAL_IPS'].append('127.0.0.1')
            settings['CORS_ORIGIN_ALLOW_ALL'] = True
            settings['CSRF_TRUSTED_ORIGINS'].extend([
                'localhost',
                'localhost:8000',
                'localhost:5000',
            ])
        return settings
