from django.forms import widgets
from hyperpython import div, input_
from django.utils.translation import ugettext_lazy as _


class FileInput(widgets.FileInput):
    """
    A custom file input widget used by all forms of ej.
    To specify wich type of file it will accept, pass 'accept'
    to attrs dict.
    E.g.: widgets.FileInput(attrs={'accept':'image/*'})
    """
    class Media:
        js = ('js/file-input.js',)

    def render(self, name, value, attrs=None, renderer=None):
        widget = self.get_context(name, value, attrs)['widget']

        w_name = widget.get('name', '')
        w_type = widget.get('type', '')
        w_attrs = widget.get('attrs', {})

        return div(class_="EJ-fileInput")[
            div(class_="PickFileButton")[
                input_(
                    style="opacity: 0",
                    type_=w_type,
                    name=w_name,
                    **w_attrs
                ),
                _("Choose a file")
            ],
            div(class_="FileStatus")[_("No file chosen")]
        ].render()


# MUDAR TRADUÇÃÕ
# "Nenhum arquivo selecionado"
# "Escolher arquivo"