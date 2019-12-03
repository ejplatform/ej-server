from boogie.configurations import MiddlewareConf as Base


class MiddlewareConf(Base):
    """
    Class responsible for the middleware that are a framework of hooks
    """
    def get_middleware(self):
        """
        Return the project Middleware
        :return: middleware
        """
        middleware = super().get_middleware()
        middleware = [
            # 'corsheaders.middleware.CorsMiddleware',
            "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
            "ej_boards.middleware.BoardFallbackMiddleware",
            *middleware,
        ]
        if "debug_toolbar" in self.INSTALLED_APPS:
            middleware = ["debug_toolbar.middleware.DebugToolbarMiddleware", *middleware]
        if self.ENVIRONMENT == "testing":
            middleware.remove("django.middleware.locale.LocaleMiddleware")
        if self.EJ_ROCKETCHAT_INTEGRATION:
            middleware.append("ej_rocketchat.middleware.ContentSecurityPolicyMiddleware")
        return middleware
