from hyperpython import render


def with_template(model, role, template=None):
    """
    Decorator Register element rendered from a template.
    """

    def decorator(func):
        nonlocal template

        if template is None:
            template = f"ej/roles/{func.__name__.replace('_', '-')}.jinja2"

        return render.register_template(model, template, role=role)(func)

    return decorator


render.with_template = with_template
