#!/usr/bin/env python3
import os
import sys
from pip._internal import main as pip_main


def get_deps(deps):
    """
    Return dependencies from an argv list.
    """
    deps = list(deps)
    while deps and not deps[0].endswith(os.path.basename(__file__)):
        del deps[0]
    return deps[1:]


def banner(msg):
    line = '=' * (len(msg) + 5)
    return '\n'.join([f'#{line}', f'# {msg}', f'#{line}\n\n'])


def main():
    print(banner('PREPARING YOUR PYTHON ENVIRONMENT'))

    # PYTHON
    print('Installing pip extra dependencies.')
    pip_main(['install', 'poetry>=0.12', *get_deps(sys.argv)])

    from poetry.console import main as poetry_main
    sys.argv = ['poetry', 'install']
    try:
        poetry_main()
    except SystemExit:
        pass

    # JAVASCRIPT (TODO)
    print(banner('PREPARING YOUR JAVASCRIPT ENVIRONMENT'))



if __name__ == '__main__':
    main()
