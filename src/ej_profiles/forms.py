from django.forms import ModelForm, DateInput

from . import models


class ProfileForm(ModelForm):
    """
    User profile form
    """

    class Meta:
        model = models.Profile
        fields = [
            'city', 'state', 'country',
            'gender', 'race', 'ethnicity',
            'political_activity', 'biography',
            'occupation', 'education', 'image'
        ]


class ProfileImageForm(ModelForm):
    class Meta:
        model = models.Profile
        fields = ['image']
