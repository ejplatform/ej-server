from boogie import rules


@rules.register_perm('ej_rocketchat.can_access_rocketchat')
def can_access_rocketchat(user):
    return (
        user.is_superuser or
        user.has_perm('ej_rocketchat.can_access_rocketchat')
    )
