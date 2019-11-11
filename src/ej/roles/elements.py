from hyperpython import div, h1, p
from hyperpython.components import wrap


def popup_content(title, text, action, **kwargs):
    """
    Content of a pop-up window.
    """
    return div(**kwargs)[h1(title), p(text), action].add_class("PopupWindow", first=True)


def paired_layout(left, right, **kwargs):
    """
    Layout that places an element to the left and a second element to the right.
    """
    return div(**kwargs)[wrap(left), wrap(right)].add_class("PairedLayout")


def paired_links(left, right, **kwargs):
    """
    Layout that places an element to the left and a second element to the right.
    """
    return paired_layout(left, right, **kwargs)


def command_bar(*actions, **kwargs):
    """
    Element that includes configuration links bellow the header bar.
    """
    action_number = len(actions)
    if action_number == 1:
        return div(actions, **kwargs).add_class("CommandBar")
    elif action_number == 2:
        return div(actions, **kwargs).add_class("CommandBar")
    else:
        raise ValueError(f"cannot include more than 2 actions, got: {action_number}")
