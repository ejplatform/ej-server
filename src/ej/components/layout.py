from typing import Mapping

from hyperpython import a, div

from ..roles.tags import icon


def tabs(items, select=0, js=True, **kwargs):
    """
    Return a tabbed interface.
    """
    return _make_tabs("tabs", js, kwargs, list(_tab_anchors(items, select)))


def categories(items, select=0, js=True, **kwargs):
    """
    Similar to tabs, but display several categories for the user to select.
    """

    return _make_tabs(
        "categories",
        js,
        kwargs,
        [
            icon("chevron-left", class_="categories__left", is_element="leftArrow:click"),
            *_tab_anchors(items, select),
            icon("chevron-right", class_="categories_right", is_element="rightArrow:click"),
        ],
    )


def _tab_anchors(items, select):
    items = items.items() if isinstance(items, Mapping) else items
    for idx, (k, v) in enumerate(items):
        args = {"href": v} if isinstance(v, str) else v
        args.update(role="tab", tabindex=0, is_selected=select == idx)
        yield a(k, **args)


def _make_tabs(cls, js, kwargs, children):
    if js:
        kwargs["is-component"] = True
    kwargs.setdefault("role", "tablist")
    return div(children, **kwargs).add_class(cls, first=True)
