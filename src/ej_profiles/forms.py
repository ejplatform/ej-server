from django.forms import ModelForm

from . import models


class ProfileForm(ModelForm):
    """
    User profile form
    """

    class Meta:
        model = models.Profile
        fields = [
            'city', 'state', 'country',
            'gender', 'race',
            'political_activity', 'biography',
            'age', 'occupation',
            'image',
        ]


class ProfileImageForm(ModelForm):
    class Meta:
        model = models.Profile
        fields = ['image']
