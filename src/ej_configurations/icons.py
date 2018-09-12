def default_icon_name(social):
    """
    Return icon from the given social network
    """
    try:
        return SOCIAL_ICONS[social.lower()]
    except KeyError:
        raise ValueError(f'unknown social network: {social}')


SOCIAL_ICONS = {
    **{net: net for net in (
        'bitbucket facebook github instagram medium pinterest telegram '
        'tumblr twitter whatsapp'.split()
    )},
    **{
        'google plus': 'google-plus-g',
        'google+': 'google-plus-g',
        'reddit': 'redit-alien',
        'stack overflow': 'stackoverflow'
    }
}
