from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from . import models
from .rocket import rocket


class RocketIntegrationForm(forms.Form):
    """
    Form that asks basic configuration about a Rocket.Chat instance.
    """

    rocketchat_url = forms.URLField(
        label=_('Rocket.Chat URL'),
        help_text=_('Required URL for Rocket.Chat admin instance.'),
        initial=settings.EJ_ROCKETCHAT_URL,
    )
    admin_username = forms.CharField(
        label=_('Username'),
        help_text=_('Username for Rocket.Chat admin user.')
    )
    admin_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label=_('Password'),
        help_text=_('Password for Rocket.Chat admin user.')
    )

    def get_config(self):
        """
        Return a saved RCConfig instance from form data.
        """
        url = self.cleaned_data['rocketchat_url']
        config = models.RCConfig(url=url)
        response = config.api_call(
            'login',
            payload={
                'username': self.cleaned_data['admin_username'],
                'password': self.cleaned_data['admin_password'],
            },
            raises=False,
        )
        print(response)
        user_id = response['data']['userId']
        auth_token = response['data']['authToken']

        # Save config
        config, _ = models.RCConfig.objects.get_or_create(url=url)
        config.admin_id = user_id
        config.admin_token = auth_token
        config.is_active = True
        config.save()
        return config


class CreateUsernameForm(forms.ModelForm):
    """
    Asks user for a new username for its Rocket.Chat account.
    """

    class Meta:
        model = models.RCAccount
        fields = ['username']

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def full_clean(self):
        super().full_clean()
        try:
            username = self.cleaned_data['username'].lstrip('@')
        except AttributeError:
            return
        try:
            self.instance = rocket.register(self.user, username)
        except ValueError as exc:
            raise ValidationError(str(exc))
