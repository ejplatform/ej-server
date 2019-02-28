from django.utils.translation import ugettext_lazy as _
from hyperpython import nav, section, Block, a
from hyperpython.components import hyperlink, html_list, fa_icon
from typing import Callable, Iterable

from ..roles import link, h1, div


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
    return nav(*sections, class_="page-menu", is_component=True)


def menu_section(name, links, **kwargs):
    """
    Wraps a list of elements into a menu section <ul>
    """
    children = [html_list(map(menu_item, links))]
    if name:
        children.insert(0, h1(name))
        kwargs.setdefault('title', str(name))
    return section(children, **kwargs)


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
page_menu.ACCESSIBILITY = thunk(lambda: menu_section(_('Accessibility'), [
    a([fa_icon('text-height'), _('Toggle Font Size')], href="#", is_element="toggleFontSize"),
    a([fa_icon('adjust'), _('Toggle Contrast'), ], href="#", is_element="toggleContrast"),
]))

#: Conversations menu
page_menu.CONVERSATION = thunk(lambda: menu_section(_('Conversations'), [
    link(_('Conversations'), href='conversation:list'),
    link(_('My Conversations'), href='boards:board-list'),
    link(_('Add Conversation'), href='boards:board-create'),
]))

#: About menu
page_menu.ABOUT = thunk(lambda: menu_section(_('About'), [
    link(_('About'), href='help:about-us'),
    link(_('Frequently Asked Questions'), href='help:faq'),
    link(_('Usage terms'), href='help:usage'),
], is_optional=True))

#: Default menu
page_menu.DEFAULT_MENU_SECTIONS = thunk(lambda: Block([
    page_menu.CONVERSATION(),
    page_menu.ABOUT(),
    page_menu.ACCESSIBILITY(),
]))
