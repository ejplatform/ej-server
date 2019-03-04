from operator import attrgetter

from django.forms import Form, ModelForm

NOT_GIVEN = object()


# TODO: move this functionality to Django-Boogie
class EjForm(Form):
    """
    Form with additional functionality.
    """

    def __init__(self, data=None, files=None, *args, request=None, **kwargs):
        if request is not None and request.method in self._meta_property('http_methods', ('POST',)):
            method = request.method
            data = getattr(request, method)
            kwargs.setdefault('files', request.FILES)
            super().__init__(data, *args, **kwargs)
            self.http_method = method
        else:
            super().__init__(*args, **kwargs)
            self.http_method = getattr(request, 'method', None)

    def _meta_property(self, prop, default=NOT_GIVEN):
        try:
            return getattr(getattr(self, 'Meta', None), prop)
        except AttributeError:
            if default is NOT_GIVEN:
                raise
            return default

    def is_valid_http(self, method):
        """
        Return true if form is valid and was submitted with the given HTTP
        method.

        Args:
            method (str or sequence): A string describing the method or a list
            of string
        """
        if self.http_method is None:
            msg = 'must be initialized with a request to use this function'
            raise RuntimeError(msg)
        if (isinstance(method, str) and self.http_method == method.upper()
            or self.http_method in map(str.upper, method)):
            return self.is_valid()
        else:
            return False

    is_valid_post = (lambda self: self.is_valid_http('POST'))
    is_valid_get = (lambda self: self.is_valid_http('GET'))
    is_valid_put = (lambda self: self.is_valid_http('PUT'))
    is_valid_patch = (lambda self: self.is_valid_http('PATCH'))
    is_valid_delete = (lambda self: self.is_valid_http('DELETE'))

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


class EjModelForm(EjForm, ModelForm):
    """
    A ModelForm version of the extended form.
    """


class PlaceholderForm(EjForm):
    """
    Add placeholders from field labels.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_widget_attributes('placeholder', from_attr='label')
