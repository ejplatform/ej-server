from collections import defaultdict

from django.utils.translation import ugettext_lazy as _
from hyperpython import nav, Block, a, div
from hyperpython.components import hyperlink, html_list, fa_icon

from ej.components.functional import thunk, split_with
from ..roles import link, h1


def page_menu(*items, request=None, caller=None, **kwargs):
    """
    Creates a new menu from a list of sections.

    Sections are separated by either Ellipsis (...) or None values.

    Args:
        accessibility (bool):
            Appends an accessibility menu items (enabled by default)
        conversation (bool):
            Enable section with the conversation pages.
        about (bool):
            Enable a section with the "About" pages (faq/about-us/usage)

    Examples:

        .. code-block:: python

            page_menu(
                # Some section (document with a comment)
                'Item name </absolute-path/>',
                'Item name <app:view-name>',
                ...,
                # Another section
                a_model_instance,  # (must implement get_absolute_url)
                anything_that_hyperpython_hyperlink_understands,

                # It accepts additional keyword arguments corresponding
                # to default section names. Menu items are inserted in order.
                accessibility=False,
            )
    """
    if len(items) == 1 and isinstance(items[0], (list, tuple)):
        items = items[0]

    groups = split_with(lambda x: x in (..., None), items)
    sections = [menu_section(None, group) for group in groups]
    if caller is not None:
        data = caller().strip()
        if data:
            sections = (*items, data)
    else:
        automatic = default_implementations(request, **kwargs)
        sections = [*sections, *automatic]

    result = menu_from_sections(sections)
    return result.render() if caller else result


def menu_from_sections(sections):
    return div(*sections, class_="page-menu", id="page-menu", is_component=True, role="menu")


def menu_section(name, links, **kwargs):
    """
    Wraps a list of elements into a menu section <ul>
    """
    children = [html_list(map(menu_item, links))]
    if name:
        children.insert(0, h1(name))
        kwargs.setdefault("title", str(name))
        kwargs.setdefault("aria-label", str(name))
    return nav(children, **kwargs)


def menu_item(item):
    if hasattr(item, "__html__"):
        return item
    else:
        return hyperlink(item)


def default_implementations(request=None, **kwargs):
    """
    Return a list of default implementations for common sections.

    See Also:
        :func:`menu` for more details.
    """
    kwargs.setdefault("about", True)
    kwargs.setdefault("accessibility", True)
    for name, value in kwargs.items():
        if name == "about" and value:
            yield page_menu.ABOUT()
        elif name == "accessibility" and value:
            yield page_menu.ACCESSIBILITY()
        else:
            raise TypeError(f"invalid parameter {name}")


#
# Sections and styles
#
def menu_links(section, request, object=None):
    """
    Return a list of links for some menu section.
    """
    try:
        render_functions = MENU_FUNCTIONS[section]
    except KeyError:
        raise ValueError(r"invalid section: {section!r}")
    for func in render_functions:
        yield from func(request, object)


def register_menu(section):
    """
    Register a function that generates links using the :func:`menu_links`
    function. The function must receive a request and a second object
    (which can be None) pertaining to that section. Ex.: in a route that
    configures the user profile, that object can be the profile object for the
    request user.
    """
    return lambda f: MENU_FUNCTIONS[section].append(f) or f


# Storage
MENU_FUNCTIONS = defaultdict(list)

#: Accessibility menu
page_menu.ACCESSIBILITY = thunk(
    lambda: menu_section(
        _("Accessibility"),
        [
            a([fa_icon("text-height"), _("Toggle Font Size")], href="#", is_element="toggleFontSize"),
            a([fa_icon("adjust"), _("Toggle Contrast")], href="#", is_element="toggleContrast"),
        ],
    )
)

#: About menu
page_menu.ABOUT = thunk(
    lambda: menu_section(
        _("About"),
        [
            link(_("About"), href="about-us"),
            link(_("Frequently Asked Questions"), href="faq"),
            link(_("Usage terms"), href="usage"),
        ],
        is_optional=True,
    )
)

#: Default menu
page_menu.DEFAULT_MENU_SECTIONS = thunk(lambda: Block([page_menu.ABOUT(), page_menu.ACCESSIBILITY()]))

#: Links
page_menu.links = menu_links
page_menu.register = register_menu

#: Create entire sections from links
page_menu.section = lambda title, ref, *args: menu_section(title, menu_links(ref))
