from hyperpython import a, i

_ = lambda x: x


def link(value, href='#', target='.Page-mainContainer', class_=(),
         action='target', instant=True, button=False, transition='cross-fade',
         preload=False, scroll=False, prefetch=False, primary=False, args=None):
    classes = [*class_]
    if button:
        classes.append('Button')

    kwargs = {
        'href': href,
        'class': classes,
        'primary': primary,
        'up-instant': instant,
        'up-restore-scroll': scroll,
        'up-preload': preload,
        'up-prefetch': prefetch,
    }
    if action:
        kwargs[f'up-{action}'] = target
    if transition:
        kwargs['up-transition'] = transition
    if args:
        for arg in args.split():
            kwargs[arg] = True
    return a(kwargs, value)


def rocket_button(value=_('Access CPA panel'), href='/talks/', **kwargs):
    return link(href=href, class_="RocketButton", **kwargs)[
        i(value, class_='fa fa-comment')
    ]


def action_button(value=_('Go!'), href='#', primary=True, **kwargs):
    return link(value, href, primary=primary, **kwargs)
