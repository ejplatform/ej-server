from django.utils.translation import ugettext_lazy as _
from hyperpython import nav
from hyperpython.components import hyperlink, html_list, fa_icon
from typing import Callable, Iterable

from ..roles import link


def page_menu(*items, request=None, **kwargs):
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
    sections = list(map(list, split_with(lambda x: x in (..., None), items)))
    automatic = default_implementations(request, **kwargs)
    return nav([*map(menu_section, sections), *automatic], class_="page-menu")


def menu_section(links, **kwargs):
    """
    Wraps a list of elements into a menu section <ul>
    """
    children = map(menu_item, links)
    return html_list(children, **kwargs).add_class("menu-section")


def menu_item(item):
    if hasattr(item, '__html__'):
        return item
    else:
        return hyperlink(item)


def default_implementations(request=None, **kwargs):
    """
    Return a list of default implementations for common sections.

    See Also:
        :func:`menu` for more details.
    """
    kwargs.setdefault('about', True)
    kwargs.setdefault('accessibility', True)
    for name, value in kwargs.items():
        if name == 'conversation' and value:
            yield page_menu.CONVERSATION()
        elif name == 'about' and value:
            yield page_menu.ABOUT()
        elif name == 'accessibility' and value:
            yield page_menu.ACCESSIBILITY()
        else:
            raise TypeError(f'invalid parameter {name}')


#
# Auxiliary functions
#
NOT_GIVEN = object()


def thunk(func, result=NOT_GIVEN):
    """
    Some objects must be implemented as thunks to avoid circular imports
    before Django is fully initialized.
    """
    if result is not NOT_GIVEN:
        value = result

    def wrapped():
        nonlocal value
        try:
            return value
        except NameError:
            value = func()
            return value

    return wrapped


def split_with(pred, lst, make_list: Callable = list):
    it = iter(lst)
    elem = make_list(take_until(pred, it))
    while elem:
        yield elem
        elem = make_list(take_until(pred, it))


def take_until(pred, it) -> Iterable:
    for x in it:
        if pred(x):
            break
        yield x


#
# Sections and styles
#

#: Accessibility menu
page_menu.ACCESSIBILITY = thunk(lambda: menu_section([
    link([fa_icon('text-height'), _('Toggle Font Size')], href="#", is_component="Page:toggleFontSize"),
    link([fa_icon('adjust'), _('Toggle Contrast'), ], href="#", is_component="Page:toggleContrast"),
]))

#: Conversations menu
page_menu.CONVERSATION = thunk(lambda: menu_section([
    link(_('My Conversations'), href='boards:board-list'),
    link(_('Add Conversation'), href='boards:board-create'),
]))

#: About menu
page_menu.ABOUT = thunk(lambda: menu_section([
    link(_('About'), href='help:about-us'),
    link(_('Frequently Asked Questions'), href='help:faq'),
    link(_('Usage terms'), href='help:usage'),
]))
