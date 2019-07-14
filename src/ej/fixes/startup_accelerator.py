"""
FIXME: Upgrade to Python 3.7 to use the lazy import functionality
TODO: make it usable. This has been useful for profiling, but it is not a serious code.
"""

import builtins

builtin_import = builtins.__import__
BLACKLIST = ["pandas._libs.tslibs.nattype"]


def make_lazy_importer(names):
    import demandimport

    slow_modules = set(names)
    sys_import = builtin_import
    lazy_import = demandimport._demandimport
    track = []
    blacklist = frozenset(BLACKLIST)

    def __import__(name, globals=None, locals=None, fromlist=None, level=0):  # noqa: N802
        track.append(name)
        base = name.split(".")[0]
        if base in slow_modules and name not in blacklist:
            # raise ValueError(name)
            if base != name or True:
                raise ValueError([x for x in track if x.startswith("ej") or x.startswith("boogie")])
            try:
                mod = lazy_import(name, globals, locals, fromlist, level)
            except KeyError:
                print("bad import:", name)
                return sys_import(name, globals, locals, fromlist, level)
        else:
            return sys_import(name, globals, locals, fromlist, level)

    return sys_import
    # return __import__


def accelerate():
    builtins.__import__ = make_lazy_importer(
        [
            # Scientific
            "numpy",
            "scipy",
            "pandas",
            "scikit",
        ]
    )
