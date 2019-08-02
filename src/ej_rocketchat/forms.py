from logging import getLogger

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from ej.forms import PlaceholderForm
from . import models
from .exceptions import ApiError
from .rocket import new_config, RCConfigWrapper

log = getLogger("ej")
User = get_user_model()
PASSWORD_MSG = _(
    """Password for Rocket.Chat admin user.
It is important to configure your Rocket.Chat instance with a unique password since
this value will be stored in plain text into Django's own database."""
)


class RocketIntegrationForm(PlaceholderForm, forms.Form):
    """
    Form that asks basic configuration about a Rocket.Chat instance.
    """

    # URLFields explicitly disallow local domains (except for localhost)
    rocketchat_url = forms.CharField(
        label=_("Rocket.Chat URL"),
        help_text=_("Required URL for Rocket.Chat admin instance."),
        initial=settings.EJ_ROCKETCHAT_URL,
    )
    api_url = forms.CharField(
        label=_("Internal URL"),
        help_text=_("Optional URL used for communication with Rocket.Chat in the internal network."),
        required=False,
    )
    username = forms.CharField(label=_("Username"), help_text=_("Username for Rocket.Chat admin user."))

    password = forms.CharField(
        widget=forms.PasswordInput, required=False, label=_("Password"), help_text=PASSWORD_MSG
    )
    config = None

    def full_clean(self):
        super().full_clean()
        if self.is_bound:
            self._clean_config(self.cleaned_data)

    def _clean_config(self, data):
        """
        Return a RCConfig instance from form data.
        """
        url = data["rocketchat_url"]
        api_url = data["api_url"] or url
        config = models.RCConfig(url=api_url)
        rocket_api = RCConfigWrapper(config)
        payload = {"username": data["username"], "password": data["password"]}
        response = rocket_api.api_call("login", payload=payload, raises=False)

        if response.get("status") == "success":
            self.config = self._make_config(response["data"])
            return config
        elif response.get("error") in ("JSONDecodeError", "ConnectionError"):
            self.add_error("rocketchat_url", _("Error connecting to server"))
        elif response.get("error", "Unauthorized"):
            self.add_error("username", _("Invalid username or password"))
        else:
            log.error(f"Invalid response: {response}")
            self.add_error(None, _("Error registering on Rocket.Chat server"))

    def _make_config(self, data):
        url = self.cleaned_data["rocketchat_url"]
        api_url = self.cleaned_data["api_url"] or ""
        user_id = data["userId"]
        auth_token = data["authToken"]

        # Save config
        config = models.RCConfig(url=url)
        config.api_url = api_url
        config.admin_id = user_id
        config.admin_token = auth_token
        config.admin_username = self.cleaned_data["username"]
        config.admin_password = self.cleaned_data["password"]
        config.is_active = True
        return config

    def save(self):
        self.config.save()


class CreateUsernameForm(PlaceholderForm, forms.ModelForm):
    """
    Asks user for a new username for its Rocket.Chat account.
    """

    class Meta:
        model = models.RCAccount
        fields = ["username"]

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def full_clean(self):
        super().full_clean()
        try:
            username = self.cleaned_data["username"].lstrip("@")
        except (KeyError, AttributeError):
            return

        try:
            self.instance = new_config().register(self.user, username)
        except ApiError as exc:
            error = exc.error_message
            if exc.value["errorType"] == "error-field-unavailable":
                if f"{username} is already in use" in error:
                    self.add_error("username", _("Username already in use."))
                elif f"{self.user.email} is already in use" in error:
                    msg = _(
                        "User with {email} e-mail already exists.\n"
                        "Please contact the system administrator."
                    )
                    self.add_error("username", msg.format(email=self.user.email))
                else:
                    self.add_error("username", _("Error: {}").format(error))
            else:
                raise
