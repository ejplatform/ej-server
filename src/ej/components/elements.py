from hyperpython import components, span
from hyperpython import div, h1, p
from hyperpython.components import a_or_span, wrap


def paragraph(title, description=None, **kwargs):
    """
    Display a centered title with a small description paragraph.

    This content is wrapped into a div that centers the content into the main
    page layout.
    """
    children = [h1(title, class_='Paragraph-title')]
    if description:
        children.append(p(description, class_='Paragraph-text'))
    return div(children, **kwargs).add_class('Paragraph', first=True)


def icon(name, href=None, **kwargs):
    """
    Generic icon function.

    If name does not end with a file extension (e.g.: .svg, .png, etc), it
    creates a font-awesome icon inside a <i> element. Otherwise, it returns
    an <img> tag pointing to the correct icon.

    If href is given, it wraps content inside an <a> tag.
    """
    if '.' in name:
        raise NotImplementedError
    else:
        return components.fa_icon(icon, href=href, **kwargs)


def decorated_text(text, icon, style=None, href=None, **kwargs):
    """
    This element is a simple text with an icon placed on the left hand side.

    If style='accent', it decorates the icon with the accent color. Style can
    also be

    href can be given towraps content inside an <a> tag.
    """
    return a_or_span(class_='DecoratedText', href=href, **kwargs)[
        _icon(icon),
        span(text)
    ]


def popup_content(title, text, action, **kwargs):
    """
    Content of a pop-up window.
    """
    return div(**kwargs)[
        h1(title),
        p(text),
        action
    ].add_class('PopupWindow', first=True)


def paired_layout(left, right, **kwargs):
    """
    Layout that places an element to the left and a second element to the right.
    """
    return div(**kwargs)[
        wrap(left),
        wrap(right),
    ].add_class('PairedLayout')


def paired_links(left, right, **kwargs):
    """
    Layout that places an element to the left and a second element to the right.
    """
    link_a = left
    link_b = right
    return paired_layout(link_a, link_b, **kwargs)


def command_bar(*actions, **kwargs):
    """
    Element that includes configuration links bellow the header bar.
    """
    if len(actions) == 1:
        return div(actions, **kwargs).add_class('CommandBar')
    elif len(actions) == 2:
        return div(actions, **kwargs).add_class('CommandBar')
    else:
        n = len(actions)
        raise ValueError(f'cannot include more than 2 actions, got: {n}')


_icon = icon
