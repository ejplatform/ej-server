from operator import attrgetter

from django.forms import Form


class RequestForm(Form):
    """
    Form with additional functionality.
    """

    http_method = None

    @classmethod
    def bind_to_request(cls, request, *args, **kwargs):
        """
        Creates a form instance from the given request. Any additional
        positional and keyword argument is passed to the function as-is.
        """
        if request.method == 'POST':
            form = cls(request.POST, *args, **kwargs)
        else:
            form = cls(*args, **kwargs)
        form.http_method = request.method
        return form

    def is_valid_post(self):
        """
        Checks if data was submitted via POST and is valid.
        """
        if self.http_method is None:
            msg = 'must be initialized with a request to use this function'
            raise RuntimeError(msg)
        if self.http_method == 'POST':
            return self.is_valid()
        else:
            return False

    def set_widget_attributes(self, attribute, value=None, from_attr=None):
        """
        Define the given attribute to all widgets in the form.
        """
        getter = from_attr and attrgetter(from_attr)
        for elem in self:
            if from_attr:
                value = getter(elem)
                elem.field.widget.attrs.setdefault(attribute, value)
            elif value is None:
                elem.field.widget.attrs.pop(attribute, None)
            else:
                elem.field.widget.attrs.setdefault(attribute, value)


class PlaceholderForm(RequestForm):
    """
    Add placeholders from field labels.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_widget_attributes('placeholder', from_attr='label')
