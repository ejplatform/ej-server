from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

User = get_user_model()


class RegistrationForm(forms.ModelForm):
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
        fields = [
            'name', 'email',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self:
            field.field.widget.attrs.update(placeholder=field.label)

    def _post_clean(self):
        super()._post_clean()
        data = self.cleaned_data
        if not (data.get('password') == data.get('password_confirm') != None):
            self.add_error('password_confirm', _('Passwords do not match'))


class LoginForm(forms.Form):
    """
    User login
    """
    if getattr(settings, 'ALLOW_USERNAME_LOGIN', settings.DEBUG):
        email = forms.CharField(label=_('E-mail'))
    else:
        email = forms.EmailField(label=_('E-mail'))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
