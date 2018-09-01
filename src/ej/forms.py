from django.forms import Form


class PlaceholderForm(Form):
    """
    Add placeholders from field labels.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self:
            field.field.widget.attrs.setdefault('placeholder', field.label)
