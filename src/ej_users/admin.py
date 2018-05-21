from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm as AuthUserChangeForm, UserCreationForm as AuthUserCreationForm
from django.utils.translation import ugettext_lazy as _

from .models import User


class UserChangeForm(AuthUserChangeForm):
    class Meta(AuthUserChangeForm.Meta):
        model = User


class UserCreationForm(AuthUserCreationForm):
    error_messages = dict(
        AuthUserCreationForm.error_messages,
        duplicate_username=_('This username has already been taken.')
    )


class Meta(AuthUserCreationForm.Meta):
    model = User


def clean_username(self):
    username = self.cleaned_data["username"]
    try:
        User.objects.get(username=username)
    except User.DoesNotExist:
        return username
    raise forms.ValidationError(self.error_messages['duplicate_username'])


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
                    ('User Profile', {'fields': (
                        'name', 'email', 'city', 'state', 'country', 'race',
                        'gender', 'occupation', 'age', 'political_movement',
                        'biography', 'image',
                    )}),
                ) + AuthUserAdmin.fieldsets
    list_display = ('username', 'name', 'email', 'is_superuser')
    search_fields = ['name', 'email', 'username']
