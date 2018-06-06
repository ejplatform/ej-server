#!/usr/bin/env python3
import contextlib
import importlib
import os
import sys
from pathlib import Path
import subprocess

BASE_PATH = Path(__file__).parent.parent.parent
mod_map = {
    'courier': 'git+https://github.com/ejplatform/django-messages-courier.git/',
    # 'ej_conversations': 'git+https://github.com/ejplatform/ej-conversations.git',
    'boogie': 'git+https://github.com/fabiommendes/django-boogie.git/',
    'hyperpython': 'git+https://github.com/fabiommendes/hyperpython.git/',
}


def git_repositories():
    with open(BASE_PATH / 'etc/requirements/git-modules.txt') as F:
        remotes = [line.strip() for line in F if not line.startswith('#')]
    locals = []

    for mod, repo in mod_map.items():
        try:
            mod_object = importlib.import_module(mod)
        except ImportError:
            pass
        else:
            package = Path(mod_object.__file__).parent
            if package_has_git(package):
                remotes.remove(repo)
                locals.append(package_repository(package))
    return remotes, locals


def package_has_git(path):
    for p in (path.parent, path.parent.parent):
        if (p / 'setup.py').exists() and (p / '.git').exists():
            return True
    return False


def package_repository(path):
    src = path.parent
    if (src / '.git').exists():
        return src
    elif (src.parent / '.git').exists():
        return src.parent
    raise ValueError('could not find a git repository: %s' % path)


@contextlib.contextmanager
def chdir(new):
    old_dir = os.getcwd()
    try:
        os.chdir(new)
        yield
    finally:
        os.chdir(old_dir)


def main():
    print('Updating volatile dependencies')

    remotes, locals = git_repositories()
    python = sys.executable

    # Install remotes
    if remotes:
        from pip.__main__ import _main as main
        print('Updating repositories directly from github.')

        remotes = ' '.join(remotes)
        main(f'{python} -m pip install {remotes}'.split)

    # Upgrade local repositories
    for local in locals:
        with chdir(local):
            print('', flush=True)
            print('Updating repository:', local)
            cmd = 'git pull --rebase origin master'

            print('  * Git update:', cmd)
            print('', flush=True)
            subprocess.run(cmd.split(), stdout=subprocess.PIPE, check=True)


if __name__ == '__main__':
    main()
