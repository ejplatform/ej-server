def conversations(queryset, user, perms):
    """
    Return a list with all conversations and
    their respective rules applied relative to
    the given user.
    """
    for obj in queryset:
        for perm in perms:
            name = perm.partition('.')[2]
            setattr(obj, name, user.has_perm(name, obj))
        yield obj
