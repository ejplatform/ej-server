def find_descriptor_name(descriptor, cls: type, hint=None):
    """
    Finds the name of the descriptor in the given class.
    """

    if hint is not None and getattr(cls, hint, None) is descriptor:
        return hint

    for attr in dir(cls):
        value = getattr(cls, attr, None)
        if value is descriptor:
            return attr
    raise RuntimeError("%r is not a member of class" % descriptor)


def fix():
    """
    Remove small bug in descriptors that prevented lazy() automatically finding
    the descriptor name of lambda functions. This should go away in the
    next version of sidekick.
    """
    from sidekick import lazy

    lazy.__globals__["find_descriptor_name"] = find_descriptor_name
