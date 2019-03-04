from typing import Mapping

from hyperpython import a, div

from ej.roles.tags import icon


def tabs(items, select=0, js=True, **kwargs):
    """
    Return a tabbed interface.
    """
    items = items.items() if isinstance(items, Mapping) else items
    children = []
    if js:
        kwargs['is-component'] = True
    for idx, (k, v) in enumerate(items):
        args = {'href': v} if isinstance(v, str) else v
        anchor = a(args, k, is_selected=select == idx)
        children.append(anchor)
    return div(children, **kwargs).add_class('tabs', first=True)


def categories(items, select=0, **kwargs):
    """
    Similar to tabs, but display several categories for the user to select.
    """
    items = items.items() if isinstance(items, Mapping) else items
    children = [icon('chevron-left', class_='categories__left',
                     is_component='categories:right')]
    for idx, (k, v) in enumerate(items):
        args = {'href': v} if isinstance(v, str) else v
        anchor = a(args, k)
        if select == idx:
            anchor = anchor.add_class('categories__selected')
        children.append(anchor)
    children.append(icon('chevron-right', class_='categories_right',
                         is_component='categories:right'))
    return div(children, **kwargs).add_class('categories')
