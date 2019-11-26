from boogie.configurations import Conf, env


class EmailConf(Conf):
    """
    E-mail settings
    """
    EMAIL_HOST = env("", name="{attr}")
    EMAIL_PORT = env(587, name="{attr}")
    EMAIL_HOST_USER = env("", name="{attr}")
    EMAIL_HOST_PASSWORD = env("", name="{attr}")
    EMAIL_USE_SSL = env(False, name="{attr}")
    EMAIL_USE_TLS = env(False, name="{attr}")
    DEFAULT_FROM_EMAIL = env("noreply@mail.ejplatform.org", name="{attr}")
    DEFAULT_FROM_NAME = env("Empurrando Juntos", name="{attr}")

    def get_email_backend(self):
        """
        Return the setting for the email
        backend accordingly to the ENVIRONMENT variable
        :return: email_backend
        """
        backend = self.env("EMAIL_BACKEND", default=None)
        if backend:
            return backend
        elif self.ENVIRONMENT == "production":
            return "django.core.mail.backends.smtp.EmailBackend"
        else:
            return "django.core.mail.backends.console.EmailBackend"
