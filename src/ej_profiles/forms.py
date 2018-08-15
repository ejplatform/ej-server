from django.forms import ModelForm, DateInput

from . import models

EDITABLE_FIELDS = ['city', 'state', 'country', 'gender', 'race', 'ethnicity', 'political_activity',
                   'biography', 'birth_date', 'occupation', 'education', 'image']


class ProfileForm(ModelForm):
    """
    User profile form
    """

    class Meta:
        model = models.Profile
        fields = EDITABLE_FIELDS
        widgets = {
            'birth_date': DateInput(attrs={'type': 'date'})
        }


class ProfileImageForm(ModelForm):
    class Meta:
        model = models.Profile
        fields = ['image']
