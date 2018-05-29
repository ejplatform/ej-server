from django import forms
from django.core.exceptions import ValidationError

from .models import VOTE_VALUES


class VoteForm(forms.Form):
    value = forms.IntegerField(required=False)
    action = forms.ChoiceField(choices=['agree', 'disagree', 'skip'], required=False)

    def get_value(self):
        if not self.is_valid():
            raise ValidationError(self.errors)

        value = self.cleaned_data["choice"]
        if value is not None:
            return value

        action = self.cleaned_data['action']
        if action:
            return VOTE_VALUES[action]
        return 0
