from django import forms
from captcha.fields import ReCaptchaField


class PushtogetherSignupForm(forms.Form):

    full_name = forms.CharField(max_length=120, label='Nome')
    captcha = ReCaptchaField(label='')

    field_order = ['full_name', 'email', 'password1', 'password2', 'capcha']

    def signup(self, request, user):

        full_name = self.cleaned_data['full_name'].split(' ', 1)

        user.first_name = full_name[0]
        if len(full_name) > 1:
            user.last_name = full_name[1]
        user.save()
