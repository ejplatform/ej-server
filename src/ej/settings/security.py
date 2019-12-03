from sidekick import unique as _unique
from boogie.configurations import SecurityConf as Base, env


class SecurityConf(Base):
    """
    Set the config for the security
    """
    INTERNAL_IPS = env([])
    AUTHENTICATION_BACKENDS = [
        "rules.permissions.ObjectPermissionBackend",
        "django.contrib.auth.backends.ModelBackend",
        "allauth.account.auth_backends.AuthenticationBackend",
    ]
    X_FRAME_OPTIONS = env("SAMEORIGIN")
    CONTENT_SECURITY_POLICY_FRAME_ANCESTORS = env([])  # TODO: deprecated
    CORS_ORIGIN_ALLOW_ALL = env(False)
    CORS_ALLOW_CREDENTIALS = env(False)

    # Configure HTTP headers
    HTTP_CONTENT_SECURITY_POLICY = env("", name="{attr}")
    HTTP_ACCESS_CONTROL_ALLOW_ORIGIN = env("", name="{attr}")
    HTTP_ACCESS_CONTROL_ALLOW_CREDENTIALS = env("", name="{attr}")
    HTTP_X_FRAME_OPTIONS = env("", name="{attr}")

    def get_cors_origin_whitelist(self, hostname):
        """
        Return the cors that are allowed to make requests
        :param hostname:
        :return:
        """
        return self.CSRF_TRUSTED_ORIGINS

    def get_csrf_trusted_origins(self, hostname):
        """
        Return the csrf
        :param hostname:
        :return: csrf
        """
        trusted = [hostname, *(self.env("DJANGO_CSRF_TRUSTED_ORIGINS", type=list) or ())]
        if self.EJ_ROCKETCHAT_INTEGRATION:
            trusted.append(remove_schema(self.EJ_ROCKETCHAT_URL))
            if self.EJ_ROCKETCHAT_API_URL:
                trusted.append(remove_schema(self.EJ_ROCKETCHAT_API_URL))
        return unique(trusted)

    def get_allowed_hosts(self, hostname):
        """
        Return the host that are allowed to acess
        :param hostname:
        :return: hosts
        """
        allowed = self.env.list("DJANGO_ALLOWED_HOSTS", default=[]) or []
        return unique([hostname, *allowed])

    def finalize(self, settings):
        """
        return the setting
        :param settings:
        :return: settings
        """
        settings = super().finalize(settings)

        if self.ENVIRONMENT == "local":
            settings["INTERNAL_IPS"].append("127.0.0.1")
            settings["CORS_ORIGIN_ALLOW_ALL"] = True
            settings["CSRF_TRUSTED_ORIGINS"].extend(
                "localhost" + x for x in ["", ":8000", ":3000", ":5000"]
            )
        return settings


def remove_schema(url):
    """
    removes the schema from a url
    :param url:
    :return: url without schema
    """
    _, _, hostname = url.partition("://")
    return hostname


def unique(data):
    """
    Return the unique data
    :param data:
    :return: unique_data
    """
    return list(_unique(data))
