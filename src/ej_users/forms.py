from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

from ej.forms import EjForm, EjModelForm

User = get_user_model()


class RegistrationForm(EjModelForm):
    """
    Register new user
    """
    password = forms.CharField(
        label=_('Password'),
        required=True,
        widget=forms.PasswordInput,
    )
    password_confirm = forms.CharField(
        label=_('Password confirmation'),
        required=True,
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ['name', 'email']
        help_texts = {k: None for k in fields}

    def _post_clean(self):
        super()._post_clean()
        data = self.cleaned_data
        if data.get('password') != data.get('password_confirm'):
            self.add_error('password_confirm', _('Passwords do not match'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self:
            field.help_text = None


class LoginForm(EjForm):
    """
    User login: email and password fields.
    """
    email_field_class = (
        forms.CharField
        if getattr(settings, 'ALLOW_USERNAME_LOGIN', settings.DEBUG)
        else forms.EmailField
    )
    email = email_field_class(label=_('E-mail'))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)


class EmailForm(EjForm):
    """
    Form with a single e-mail field.
    """

    email = forms.EmailField(label=_('E-mail'))

class RemoveAccountForm(EmailForm):
    """
    E-mail + confirmation checkbox.
    """

    confirm = forms.BooleanField(label=_('Yes, I understand the consequences.'))


class NewPasswordForm(EjForm):
    """
    Recover User Password
    """

    new_password = forms.CharField(
        label=_('Password'),
        required=True,
        widget=forms.PasswordInput,
    )
    new_password_confirm = forms.CharField(
        label=_('Password confirmation'),
        required=True,
        widget=forms.PasswordInput,
    )

    def _post_clean(self):
        super()._post_clean()
        data = self.cleaned_data
        if data.get('new_password') != data.get('new_password_confirm'):
            self.add_error('new_password_confirm', _('Passwords do not match'))
