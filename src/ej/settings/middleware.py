from boogie.configurations import MiddlewareConf as Base


class MiddlewareConf(Base):
    def get_middleware(self):
        middleware = super().get_middleware()
        middleware = [
            'corsheaders.middleware.CorsMiddleware',
            'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
            'ej_boards.middleware.BoardFallbackMiddleware',
            *middleware,
        ]
        if self.DEBUG:
            middleware = [
                'debug_toolbar.middleware.DebugToolbarMiddleware',
                *middleware
            ]
        if self.ENVIRONMENT == 'testing':
            middleware.remove('django.middleware.locale.LocaleMiddleware')
        return middleware
