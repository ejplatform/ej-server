from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm

User = get_user_model()


class ProfileForm(ModelForm):
    """
    User profile form
    """

    class Meta:
        model = User
        fields = [
            'name', 'email',
            'city', 'state', 'country',
            'gender', 'race',
            'political_movement', 'biography',
            'age', 'occupation',
        ]


class RegistrationForm(ModelForm):
    """
    Register new user
    """
    password_second = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'name', 'email', 'password',
        ]


class LoginForm(ModelForm):
    """
    User login
    """
    is_passwordless = forms.BooleanField()

    class Meta:
        model = User
        fields = [
            'email',
            'password'
        ]


class ProfileImageForm(ModelForm):
    class Meta:
        model = User
        fields = ['image']
