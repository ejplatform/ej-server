from django import forms
from django.template.loader import get_template

from ej.forms import EjModelForm
from ej.utils.widgets import FileInput
from . import models


class PaletteWidget(forms.RadioSelect):
    template_name = 'ej_boards/includes/palette-select.jinja2'
    renderer = get_template(template_name)

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return self.renderer.render(context)


class BoardForm(EjModelForm):
    class Meta:
        model = models.Board
        fields = ['title', 'description', 'slug', 'palette', 'image']
        widgets = {'palette': PaletteWidget, 'image': FileInput}
