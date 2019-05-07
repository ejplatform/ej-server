from hyperpython import a
from sidekick import import_later

urls = import_later("django.urls")


class Url(str):
    """
    A specialized string class that represents urls.
    """

    def __init__(self, url):
        self.url = str(url)

    def __truediv__(self, other):
        try:
            if self.endswith("/") or other.startswith("/"):
                sep = ""
            else:
                sep = "/"
            return Url(self.url + sep + str(other))
        except AttributeError:
            return NotImplementedError

    def __repr__(self):
        return f"Url({self.url!r})"

    def anchor(self, name, **kwargs):
        """
        Return an Hyperpython anchor object using url as href.

        It must pass the anchor contents as the first argument. It also accepts
        a additional attributes as keyword arguments.
        """
        return a(name, href=self.url, **kwargs)


class SafeUrl(Url):
    """
    Similar to Url, but it is initialized from a Django url name + attributes
    instead of the raw url value.
    """

    def __new__(cls, ref, *args, **kwargs):
        url = urls.reverse(ref, args=args, kwargs=kwargs)
        new = Url.__new__(cls, url)
        new.url = url
        return new

    def __init__(self, ref, *args, **kwargs):
        self.ref = ref
        self.url_args = args
        self.url_kwargs = kwargs
        super().__init__(self.url)

    def __repr__(self):
        all_args = ", ".join(self._repr_args())
        return f"SafeUrl({all_args})"

    def _repr_args(self):
        yield repr(self.ref)
        yield from map(repr, self.url_args)
        yield from (f"{k}={v!r}" for k, v in self.url_kwargs.items())
