from boogie.configurations import MiddlewareConf as Base


class MiddlewareConf(Base):
    def get_middleware(self):
        middleware = [
            'corsheaders.middleware.CorsMiddleware',
            *super().get_middleware(),
        ]
        if self.ENVIRONMENT == 'local':
            middleware = [
                'debug_toolbar.middleware.DebugToolbarMiddleware',
                *middleware
            ]
        elif self.ENVIRONMENT == 'testing':
            middleware.remove('django.middleware.locale.LocaleMiddleware')
        return middleware
