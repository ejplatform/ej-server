def descr(msg):
    """Mark the short_description attribute of decorated method."""
    return lambda f: setattr(f, "short_description", msg) or f


def register_actions(target_cls):
    """
    Register all functions defined in decorated class as extra actions in the
    given target class.
    """
    actions = getattr(target_cls, 'actions', [])

    def decorator(source_cls):
        for k, v in vars(source_cls).items():
            if k.startswith('__'):
                continue
            elif not k.startswith('_'):
                actions.append(k)
            setattr(target_cls, k, v)
        return source_cls

    return decorator
