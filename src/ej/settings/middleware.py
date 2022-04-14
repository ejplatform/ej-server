from boogie.configurations import MiddlewareConf as Base


class MiddlewareConf(Base):
    def get_middleware(self):
        middleware = super().get_middleware()
        middleware = [
            "django.middleware.csrf.CsrfViewMiddleware",
            "corsheaders.middleware.CorsMiddleware",
            "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
            "ej_boards.middleware.BoardFallbackMiddleware",
            "ej_conversations.integrations_middleware.KeepQueryParamsAfterLoginRedirect",
            *middleware,
        ]
        if "debug_toolbar" in self.INSTALLED_APPS:
            middleware = ["debug_toolbar.middleware.DebugToolbarMiddleware", *middleware]
        if self.ENVIRONMENT == "testing":
            middleware.remove("django.middleware.locale.LocaleMiddleware")
        return middleware
