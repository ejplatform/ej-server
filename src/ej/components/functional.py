from typing import Callable, Iterable

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
