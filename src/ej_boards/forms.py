from django import forms
from . import models
from ej.forms import PlaceholderForm


class BoardForm(PlaceholderForm, forms.ModelForm):
    class Meta:
        model = models.Board
        fields = ['slug', 'title', 'description']


class BoardSlugForm(PlaceholderForm, forms.ModelForm):
    class Meta:
        model = models.Board
        fields = ['slug']
