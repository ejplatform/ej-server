from boogie.configurations import MiddlewareConf as Base


class MiddlewareConf(Base):
    def get_middleware(self):
        middleware = super().get_middleware()
        middleware = [
            'corsheaders.middleware.CorsMiddleware',
            'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
            'ej_users.middleware.UserFallbackMiddleware',
            *middleware,
        ]
        if self.ENVIRONMENT == 'local':
            middleware = [
                'debug_toolbar.middleware.DebugToolbarMiddleware',
                *middleware
            ]
        elif self.ENVIRONMENT == 'testing':
            middleware.remove('django.middleware.locale.LocaleMiddleware')
        return middleware
