from django.conf import settings
from django.forms import DateInput

import ej.forms
from ej.forms import EjModelForm
from . import models

EDITABLE_FIELDS = [
    'occupation', 'education',
    'gender', 'race', 'ethnicity',
    'birth_date',
    'city', 'state', 'country',
    'political_activity', 'biography',
    'profile_photo',
]
EXCLUDE_EDITABLE_FIELDS = settings.EJ_EXCLUDE_PROFILE_FIELDS


class UsernameForm(EjModelForm):
    class Meta:
        model = models.User
        fields = ['name']
        help_texts = {'name': ''}


class ProfileForm(EjModelForm):
    """
    User profile form
    """

    class Meta:
        model = models.Profile
        fields = [field for field in EDITABLE_FIELDS if field not in EXCLUDE_EDITABLE_FIELDS]
        widgets = {
            'birth_date': DateInput(attrs={'type': 'date'}),
            'profile_photo': ej.forms.FileInput(attrs={'accept': 'image/*'})
        }

    def __init__(self, *args, instance, **kwargs):
        super().__init__(*args, instance=instance, **kwargs)
        self.user_form = UsernameForm(*args, instance=instance.user, **kwargs)
        self.fields = {**self.user_form.fields, **self.fields}
        self.initial.update(self.user_form.initial)

    def save(self, commit=True, **kwargs):
        result = super().save(commit=commit, **kwargs)
        self.user_form.instance = result.user
        self.user_form.save(commit=commit)
        return result
