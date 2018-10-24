from django import forms
from django.utils.text import slugify
from . import models


class BoardForm(forms.ModelForm):
    class Meta:
        model = models.Board
        fields = ['slug', 'title', 'description']

    def _save(self, commit=True):
        instance = super(BoardForm, self).save(commit=False)
        instance.slug = slugify(instance.slug)
        if commit:
            instance.save()
        return instance
