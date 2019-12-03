from django.db.models import Model
from hyperpython import html, div, h2, span, Text, Block
from hyperpython.components import fa_icon, html_list

from ..utils import title as _title


@html.register(object, role="collapsible")
def render_collapsible(data, title=None, collapsed=False):

    """
    Renders a collapsible content.

    """

    angle = fa_icon("angle-up", class_="collapsible__handle")

    return div(
        class_ = "collapsible",
        is_component = True,
        is_collapsed = collapsed,
        children = [h2([title, angle], class_="collapsible__title"), div(data, class_="collapsible__data")],
    )


@html.register(object, role="collapsible-list")
def render_collapsible_list(_list, item_role="list-item", title=None, **kwargs):

    """
    Renders a queryset or list of objects

    Args:
        _list:
            List or queryset of objects inside the collapsible list.
        item_role:
            Role assigned to each element in the list. Defaults to
            'list-item'.
        title (bool):
            Title in which the list of object is displayed.
        expanded (str):
            If true, start list in the "expanded" state.

    """

    list__size = len(_list)
    title = _title(_list) if title is None else title
    title = Block([title, span(f" ({list_size})", class_="text-accent")])
    list_items = [html(x, item_role, **kwargs) for x in _list]
    data = html_list(list_items, class_="list-reset")
    
    return render_collapsible(data, title=title)


@html.register(Model)
def render_model(_object, role=None, request=None):
    return Text(str(_object))

