from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from ej.forms import PlaceholderForm

User = get_user_model()


class RegistrationForm(PlaceholderForm, forms.ModelForm):
    """
    Register new user
    """
    password = forms.CharField(
        label=_('Password'),
        required=True,
        widget=forms.PasswordInput,
        help_text=_('Your password')
    )
    password_confirm = forms.CharField(
        label=_('Password confirmation'),
        required=True,
        widget=forms.PasswordInput,
        help_text=_('Confirm your password')
    )

    class Meta:
        model = User
        fields = ['name', 'email']

    def _post_clean(self):
        super()._post_clean()
        data = self.cleaned_data
        if data.get('password') != data.get('password_confirm'):
            self.add_error('password_confirm', _('Passwords do not match'))

    def as_p(self):
        pass


class LoginForm(PlaceholderForm, forms.Form):
    """
    User login
    """

    if getattr(settings, 'ALLOW_USERNAME_LOGIN', settings.DEBUG):
        email = forms.CharField(label=_('E-mail'), help_text=_('Your e-mail'))
    else:
        email = forms.EmailField(label=_('E-mail'))
    password = forms.CharField(label=_('Password'),
                               widget=forms.PasswordInput,
                               help_text=_('Your password'))
