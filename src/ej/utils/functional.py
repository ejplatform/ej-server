from logging import getLogger

from sidekick import lazy, extract_function

log = getLogger("ej")


def deprecate_lazy(func, msg):
    """
    Like sidekick.lazy, but shows a deprecation message before computing function.
    """
    func = extract_function(func)

    def deprecated_func(self):
        log.warning(msg)
        return func(self)

    return lazy(deprecated_func)
