import importlib
import sys
import threading
import types

import sidekick as sk

CACHED_MODULES = {}


class LazyModule(types.ModuleType):
    def __init__(self, name):
        super().__init__(name.split('.')[-1])
        self.__file__ = '<lazy>'
        self.__path__ = name
        self.__name = name
        self.__started = False
        self.__mod = None

    def __getattr__(self, item):
        print(item)
        if self.__started:
            raise AttributeError(item)
        self.__start()
        return super().__getattr__(item)

    def __start(self):
        self.__started = True
        modules = sys.modules
        new_modules = dict(modules)
        del new_modules[self.__name]
        try:
            sys.modules = new_modules
            self.__mod = importlib.import_module(self.__name)
            for k, v in self.__mod.__dict__.items():
                setattr(self, k, v)
        finally:
            sys.modules = modules

        try:
            self.__class__ = self.__mod.__class__
        except TypeError:
            pass

        for name, mod in new_modules.items():
            if name not in modules:
                modules[name] = mod

        print('mod', self.__mod)


def defer_import(mod_name):
    sys.modules[mod_name] = LazyModule(mod_name)
    return

    n_calls = 0
    lock = threading.Semaphore()
    sys_modules = sys.modules

    @sk.deferred
    def deferred_module():
        nonlocal n_calls

        # with lock:
        new_modules = dict(sys_modules)
        try:
            del new_modules[mod_name]
            sys.modules = new_modules
            sys_modules[mod_name] = mod = importlib.import_module(mod_name)
        finally:
            sys.modules = sys_modules
        return mod

    sys.modules[mod_name] = deferred_module


def defer_import_list(lst):
    for mod in lst:
        defer_import(mod)


def accelerate():
    defer_import_list(SLOW_MODULES)


#
# List of known slow modules
#
SLOW_MODULES = [
    # Web

    # Scientific
    'numpy', 'scipy', 'pandas',
]
