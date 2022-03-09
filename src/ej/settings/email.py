from boogie.configurations import Conf
import os


class EmailConf(Conf):

    #
    # E-mail settings
    #
    DEFAULT_FROM_EMAIL = os.environ.get("SMTP_DEFAULT_EMAIL", "noreply@mail.ejplatform.org")
    SERVER_EMAIL = os.environ.get("SMTP_HOST_EMAIL", "user@mail.com")
    EMAIL_USE_TLS = True
    EMAIL_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    EMAIL_PORT = os.environ.get("SMTP_PORT", 587)
    EMAIL_HOST_USER = os.environ.get("SMTP_HOST_EMAIL", "user@mail.com")
    EMAIL_HOST_PASSWORD = os.environ.get("SMTP_HOST_PASSWORD", "password")
    DEFAULT_FROM_NAME = os.environ.get("SMTP_DEFAULT_NAME", "Empurrando Juntos")

    def get_email_backend(self):
        return "django.core.mail.backends.smtp.EmailBackend"
