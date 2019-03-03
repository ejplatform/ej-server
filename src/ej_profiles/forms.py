from django.conf import settings
from django.forms import DateInput

from ej.forms import EjModelForm
from ej.utils import widgets as ej_widgets
from . import models

EDITABLE_FIELDS = ['city', 'state', 'country', 'gender', 'race', 'ethnicity', 'political_activity',
                   'biography', 'birth_date', 'occupation', 'education', 'profile_photo']
EXCLUDE_EDITABLE_FIELDS = settings.EJ_EXCLUDE_PROFILE_FIELDS


class UsernameForm(EjModelForm):
    class Meta:
        model = models.User
        fields = ['name']
        help_texts = {
            'name': '',
        }


class ProfileForm(EjModelForm):
    """
    User profile form
    """

    class Meta:
        model = models.Profile
        fields = [field for field in EDITABLE_FIELDS if field not in EXCLUDE_EDITABLE_FIELDS]
        widgets = {
            'birth_date': DateInput(attrs={'type': 'date'}),
            'profile_photo': ej_widgets.FileInput(attrs={'accept': 'image/*'})
        }


class ProfileImageForm(EjModelForm):
    class Meta:
        model = models.Profile
        fields = ['profile_photo']
