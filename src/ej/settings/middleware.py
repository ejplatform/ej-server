from boogie.configurations import MiddlewareConf as Base


class MiddlewareConf(Base):
    def get_middleware(self):
        middleware = super().get_middleware()
        if self.ENVIRONMENT == 'local':
            middleware = ['debug_toolbar.middleware.DebugToolbarMiddleware', *middleware]
        return middleware
