import logging
from typing import Mapping

from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils.translation import ugettext_lazy
from hyperpython import a, h1, p, div, components, strong, dl, dt, dd
from hyperpython import h, html
from hyperpython.components import html_table, html_list, html_map, a_or_span
from hyperpython.renderers.attrs import render_attrs

from ej.utils.url import Url

static = staticfiles_storage.url
lazy_string_class = type(ugettext_lazy("hello"))
log = logging.getLogger("ej")
_ = lambda x: x

__all__ = [
    # Hyperpython components
    "h",
    "html_table",
    "html_list",
    "html_map",
    # EJ components
    "link",
    "link_attrs",
    "action_button",
    "intro",
    "span_icon",
    "progress_bar",
    "extra_content",
    "overlay",
    "popup",
    "toast",
    "description",
]


def link(value, href="#", target="body", **kwargs):
    return a(link_kwargs(href=href, target=target, **kwargs), [value])


def link_attrs(href="#", target="body", **kwargs):
    return render_attrs(link_kwargs(href=href, target=target, **kwargs))


def link_kwargs(href="#", action=None, args=(), **kwargs):
    kwargs = {
        "href": _normalize_href(href, kwargs.pop("url_args", None), kwargs.pop("query", None)),
        "class": _normalize_class(kwargs),
        "up-instant": kwargs.pop("instant", True),
        "up-restore-scroll": kwargs.pop("scroll", False),
        "up-preload": kwargs.pop("preload", False),
        "up-prefetch": kwargs.pop("prefetch", False),
        **{k.replace("_", "-"): v for k, v in kwargs.items()},
    }

    if action:
        kwargs[f"up-{action}"] = kwargs.pop("target", "body")
    if kwargs.get("transition"):
        kwargs["up-transition"] = kwargs.pop("transition", "cross-fade")
    for arg in args.split() if isinstance(args, str) else args:
        kwargs[arg] = True

    return kwargs


def _normalize_href(href, url_args, query):
    if isinstance(href, Url):
        href = str(href)
    elif href.startswith("/"):
        raise ValueError(
            "Do not use absolute urls in the link function (%s)."
            "Prefer using view function names such as auth:login instead of "
            "/login/. You can also wrap the url into a ej.utils.Url instance "
            "if you want to return a calculated url value." % href
        )
    elif href == "#" or href is None:
        href = "#"
    elif href.startswith("http"):
        href = href
    else:
        href = reverse(href, kwargs=url_args)

    if query is not None:
        query = "&".join(f"{k}={v}" for k, v in query.items())
        href = f"{href}?{query}"
    return href


def _normalize_class(kwargs):
    cls = kwargs.pop("class", kwargs.pop("class_", ()))
    if isinstance(cls, str):
        cls = tuple(cls.split())
    button = kwargs.pop("button", False)

    if button and cls:
        cls = (*cls, "button")
    elif button:
        cls = ("button",)
    if kwargs.pop("primary", False):
        cls = (*cls, "is-primary")
    if kwargs.pop("secondary", False):
        cls = (*cls, "is-secondary")
    return cls or None


def action_button(value=_("Go!"), href="#", primary=True, **kwargs):
    return link(value, href, primary=primary, **kwargs).add_class("button")


@html.register(lazy_string_class)
def _render_lazy_string(st, **kwargs):
    return html(str(st))


#
# Special EJ ui elements
#
def icon(name, href=None, icon_description=None, **kwargs):
    """
    Generic icon function.

    If name does not end with a file extension (e.g.: .svg, .png, etc), it
    creates a font-awesome icon inside a <i> element. Otherwise, it returns
    an <img> tag pointing to the correct icon.

    If href is given, it wraps content inside an <a> tag.
    """
    if "." in name:
        raise NotImplementedError
    else:
        if icon_description:
            kwargs["aria-label"] = icon_description
        return components.fa_icon(name, href=href, **kwargs)


def intro(title, description=None, **kwargs):
    """
    Display a centered title with a small description paragraph.

    This content is wrapped into a div that centers the content into the main
    page layout.
    """
    children = [h1(title)]
    if description:
        children.append(p(description))
    return div(children, **kwargs).add_class("intro-paragraph", first=True)


def span_icon(text, icon=None, icon_description=None, **kwargs):
    """
    This element is a simple text with an icon placed on the left hand side.

    If style='accent', it decorates the icon with the accent color. Style can
    also be

    href can be given towraps content inside an <a> tag.
    """
    text = "" if text is None else str(text)
    kwargs["children"] = [_icon(icon, icon_description=icon_description), text] if icon else [text]
    return a_or_span(**kwargs).add_class("span-icon")


def extra_content(title, text, icon=None, **kwargs):
    """
    Simple element with a title and a small paragraph with information.

    Used, for instance, in the detail page of conversations to link the
    comment form or cluster information.

    Args:
        title: Title of the content
        text: Paragraph that follows content.
        icon: Optional icon to be included with title element.

    Returns:

    """
    title = h1([_icon(icon), title]) if icon else h1(title)
    return div([title, text], **kwargs).add_class("extra-content")


def progress_bar(*args):
    """
    Display a progress bar.

    progress_bar(pc)       --> tell a percentage
    progress_bar(n, total) --> pass the number of items and total
    """

    # Compute fractions
    if len(args) == 1:
        pc = args[0]
        n = total = None
    else:
        e = 1e-50
        n, total = args
        pc = round(100 * (n + e) / (total + e))

    # Build children
    children = [
        strong(f"{pc}%", class_="block margin-r2"),
        div(
            class_="progress-bar__progress",
            aria_hidden="true",
            children=[
                div(" ", class_="color-brand-lighter", style=f"flex-grow: {pc + 3};"),
                div(" ", style=f"flex-grow: {100 - pc};"),
            ],
        ),
    ]

    if total is not None:
        children.append(div([strong(n), "/", total]))

    # Return
    return div(children, class_="progress-bar", aria_hidden="true")


def popup(title, content, action=None, **kwargs):
    """
    Return a popup screen.

    It does not include positioning and the overlay element.

    Args:
        title: Title of the popup.
        content: HTML or text content of the popup.
        action: Action button. Can be an anchor or other element.
    """
    return div(
        [
            icon("times-circle", class_="popup__close", is_component="popup:close"),
            div(
                [h1([title], class_="title"), p(content), action and div(action)], class_="popup__contents"
            ),
        ],
        **kwargs,
    ).add_class("popup")


def overlay(data, **kwargs):
    """
    Creates a popup overlay and includes the element inside
    the overlay.
    """
    return div(data, **kwargs).add_class("overlay")


def toast(icon, title, description=None, **kwargs):
    """
    Toast component: display some title with a highlighted icon.
    """
    body = [h1(title)]
    if description:
        body.append(p(description))
    return div([_icon(icon, class_="toast__icon"), div(body, class_="toast__content")], **kwargs).add_class(
        "toast"
    )


def description(items, **kwargs):
    """
    A description list.

    Can receive a dictionary or a list of tuples.
    """
    items = items.items() if isinstance(items, Mapping) else items
    children = []
    for k, v in items:
        children.extend([dt(k), dd(v)])
    return dl(children, **kwargs).add_class("description")


_icon = icon
