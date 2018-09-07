from django.forms import Form
from django.http.request import HttpRequest


class RequestForm(Form):
    """
    Form with additional functionality.
    """

    http_method = None

    @classmethod
    def bind(cls, request, *args, **kwargs):
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

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], HttpRequest):
            self.request, *args = args
            if self.request.method == 'POST':
                args = (self.request.POST, *args)
        super().__init__(*args, **kwargs)

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


class PlaceholderForm(RequestForm):
    """
    Add placeholders from field labels.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self:
            field.field.widget.attrs.setdefault('placeholder', field.label)
