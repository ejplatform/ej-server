from django.forms import ModelForm, DateInput
from django.conf import settings

from . import models

EDITABLE_FIELDS = ['city', 'state', 'country', 'gender', 'race', 'ethnicity', 'political_activity',
                   'biography', 'birth_date', 'occupation', 'education', 'image']
EXCLUDE_EDITABLE_FIELDS = settings.EJ_EXCLUDE_PROFILE_FIELDS


class UsernameForm(ModelForm):

    class Meta:

        model = models.User
        fields = ['name']
        help_texts = {
            'name': '',
        }


class ProfileForm(ModelForm):
    """
    User profile form
    """

    class Meta:

        model = models.Profile
        fields = [field for field in EDITABLE_FIELDS if field not in EXCLUDE_EDITABLE_FIELDS]
        widgets = {
            'birth_date': DateInput(attrs={'type': 'date'})
        }


class ProfileImageForm(ModelForm):
    class Meta:
        model = models.Profile
        fields = ['image']
