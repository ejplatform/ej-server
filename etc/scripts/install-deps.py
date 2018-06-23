#!/usr/bin/env python3
import contextlib
import os
import sys
import subprocess
from pathlib import Path

python = sys.executable
BASE_PATH = Path(__file__).parent.parent.parent
LOCAL = BASE_PATH / 'local'
VENDOR = LOCAL / 'vendor'
mod_map = {
    # 'ej_conversations': 'https://github.com/ejplatform/ej-conversations.git/',
    'courier': 'https://github.com/ejplatform/django-messages-courier.git/',
    'boogie': 'https://github.com/fabiommendes/django-boogie.git/',
    'hyperpython': 'https://github.com/fabiommendes/hyperpython.git/',
}


def repo_dir(uri):
    return uri.rstrip('/').rpartition('/')[-1][:-4]


@contextlib.contextmanager
def chdir(new):
    old_dir = os.getcwd()
    try:
        os.chdir(new)
        yield
    finally:
        os.chdir(old_dir)


def ensure_dirs(*paths):
    for path in paths:
        if not path.exists():
            os.mkdir(path)


def run(cmd):
    print(f'$ {cmd}', flush=True)
    subprocess.run(cmd.split(), stdout=subprocess.PIPE, check=True)
    print(end='', flush=True)


def main():
    print('Updating volatile dependencies'.upper())
    print('Dependencies are stored in the local/vendor/* folder. Remove this\n'
          'folder if you need reset your volatile dependencies\n')
    ensure_dirs(LOCAL, VENDOR)

    for mod, uri in mod_map.items():
        print(f'Verifying {mod}...')
        path = Path(os.path.abspath(VENDOR / repo_dir(uri)))
        if path.exists():
            print('\nUpdating repository')
            with chdir(path):
                run('git checkout master')
                run('git pull --rebase origin master')
        else:
            print('\nCloning repository')
            with chdir(VENDOR):
                run(f'git clone {uri}')
            with chdir(path):
                run(f'{python} setup.py develop')


if __name__ == '__main__':
    main()
