from django.forms import ModelForm, DateInput

from . import models

class DateInput(forms.DateInput):
    input_type = 'date'

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
            'birth_date', 'occupation',
            'image'
        ]
        widgets = {
            'birth_date': DateInput(attrs={'type': 'date'})
        }


class ProfileImageForm(ModelForm):
    class Meta:
        model = models.Profile
        fields = ['image']
