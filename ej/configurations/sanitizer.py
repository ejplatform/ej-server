import bleach

#
# List of valid tags to pass through the sanitizer
#
TAG_WHITELIST = bleach.ALLOWED_TAGS + [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6' 'img', 'div', 'span', 'p',
]

#
# Valid attributes in each tag
#
attrs = bleach.ALLOWED_ATTRIBUTES
ATTR_WHITELIST = dict(attrs, **{
    'a': attrs['a'] + ['up-target', 'up-modal', 'up-instant', 'up-preload', 'up-prefetch']
})
del attrs


def sanitize_html(html):
    """
    Convert a string of user HTML in safe html.
    """
    return bleach.clean(html, tags=TAG_WHITELIST, attributes=ATTR_WHITELIST)
