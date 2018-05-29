"""
Generic classes that are likely to leave this app and eventually go to
a separate library.
"""

from django.urls import reverse
from rest_framework import serializers


class HasLinksSerializer(serializers.HyperlinkedModelSerializer):
    links = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context['request']
        self.url_prefix = f'{request.scheme}://{request.get_host()}'

    def get_detail_url_name(self):
        """
        The Django-name for the detail url for the current resource.

        This is usually "<model-name>-detail"
        """
        return self.Meta.model.__name__.lower() + '-detail'

    def get_self_url_path(self, obj):
        """
        Return the absolute path (i.e., without the http://host part)
        of the detail url for the current resource.
        """
        url_name = self.get_detail_url_name()
        lookup_field = (
            getattr(self.Meta, 'extra_kwargs', {})
                .get('url', {})
                .get('lookup_field', 'pk')
        )
        lookup_value = getattr(obj, lookup_field)
        return reverse(url_name, kwargs={lookup_field: lookup_value})

    def get_links(self, obj):
        """
        Return the links dictionary mapping resource names to their
        corresponding links according to HATEAOS.
        """
        # Create default payload
        self_path = self.get_self_url_path(obj)
        self_uri = self.url_prefix + self_path
        payload = {'self': self_uri}

        # Fill inner links
        inner_links = self.get_inner_links(obj)
        if inner_links:
            if hasattr(inner_links, 'items'):
                inner_links = inner_links.items()
            else:
                inner_links = [(x, x) for x in inner_links]
            payload.update((name, join_url(self_uri, path))
                           for name, path in inner_links)
        return payload

    def get_inner_links(self, obj):
        """
        Return a dictionary or list of inner resources for the current object.

        If, for instance get_inner_links() returns {'foo': 'foo'}, it will
        create serialization like::

            {
                "links": {
                    "self": "http://my-site/api/resource/id/",
                    "foo": "http://my-site/api/resource/id/foo",
                }
                ...,
            }
        """
        return ()


class HasAuthorSerializer(HasLinksSerializer):
    author_name = serializers.SerializerMethodField()

    def get_links(self, obj):
        payload = super().get_links(obj)

        # Insert author url as an absolute url
        url_path = reverse('user-detail',
                           kwargs={'username': obj.author.username})
        payload['author'] = self.url_prefix + url_path
        return payload

    def get_author_name(self, obj):
        author = obj.author
        return author.get_full_name() or author.username


class AuthorAsCurrentUserMixin:
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


def join_url(head, *args):
    """
    Join url parts. It prevents duplicate backslashes when joining url
    elements.
    """
    if not args:
        return head
    else:
        tail = join_url(*args)
        return f"{head.rstrip('/')}/{tail.lstrip('/')}"


def validation_error(err, status_code=403):
    """
    Return a JSON message describing a validation error.
    """
    errors = err.messages
    msg = {'status_code': status_code, 'error': True}
    if len(errors) == 1:
        msg['message'] = errors[0]
    else:
        msg['messages'] = errors
    return msg
