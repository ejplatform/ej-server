from boogie.configurations import Conf, env


class EmailConf(Conf):

    #
    # E-mail settings
    #
    EMAIL_HOST = env("", name="EMAIL_HOST")
    EMAIL_PORT = env(587, name="EMAIL_PORT")
    EMAIL_HOST_USER = env("", name="EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env("", name="EMAIL_HOST_PASSWORD")
    EMAIL_USE_SSL = env(False, name="EMAIL_USE_SSL")
    EMAIL_USE_TLS = env(False, name="EMAIL_USE_TLS")
    DEFAULT_FROM_EMAIL = "noreply@mail.ejplatform.org"
    DEFAULT_FROM_NAME = env("Empurrando Juntos")

    def get_email_backend(self):
        if self.ENVIRONMENT == "production":
            backend = self.env('EMAIL_BACKEND', default=None)
            if backend:
                return backend
            return "django.core.mail.backends.smtp.EmailBackend"
        else:
            return "django.core.mail.backends.console.EmailBackend"
