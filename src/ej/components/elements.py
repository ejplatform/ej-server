from hyperpython import div, h1, p


def paragraph(title, description, **kwargs):
    """
    Display a centered title with a small description paragraph.

    This content is wrapped into a div that centers the content into the main
    page layout.
    """
    return div(**kwargs).add_class('MiniContent')[
        h1(title, class_='MiniContent-title'),
        p(description, class_='MiniContent-paragraph'),
    ]


def icon(name, href=None, **kwargs):
    """
    Generic icon function.

    If name does not end with a file extension (e.g.: .svg, .png, etc), it
    creates a font-awesome icon inside a <i> element. Otherwise, it returns
    an <img> tag pointing to the correct icon.

    If href is given, it wraps content inside an <a> tag.
    """


def decorated_text(text, icon, style=None, href=None, **kwargs):
    """
    This element is a simple text with an icon placed on the left hand side.

    If style='accent', it decorates the icon with the accent color. Style can
    also be

    href can be given towraps content inside an <a> tag.
    """


def popup_content(title, text, action, **kwargs):
    """
    Content of a pop-up window.
    """


def paired_layout(left, right, **kwargs):
    """
    Layout that places an element to the left and a second element to the right.
    """


def paired_links(left, right, **kwargs):
    """
    Layout that places an element to the left and a second element to the right.
    """


def command_bar(*actions, **kwargs):
    """
    Element that includes configuration links bellow the header bar.
    """
