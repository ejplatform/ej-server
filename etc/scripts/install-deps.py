#!/usr/bin/env python3
import contextlib
import os
import subprocess
import sys
from importlib.util import find_spec
from pathlib import Path

if len(sys.argv) >= 2 and sys.argv[-2] == '--path':
    VENDOR = Path(sys.argv[-1])
else:
    python = sys.executable
    BASE_PATH = Path(os.path.abspath(Path(__file__).parent.parent.parent))
    LOCAL = BASE_PATH / 'local'
    VENDOR = LOCAL / 'vendor'
mod_map = {
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


def ensure_dir(path):
    for sub in reversed([path, *map(Path, path.parts)]):
        if not sub.exists():
            os.mkdir(sub)


def run(cmd):
    print(f'$ {cmd}', flush=True)
    status, out = subprocess.getstatusoutput(cmd)
    print(out, flush=True)
    if status != 0:
        raise RuntimeError(f'exited with non-zero status: {status}')


def main():
    print('Updating volatile dependencies')
    print('Dependencies are stored in the local/vendor/* folder. Remove this\n'
          'folder if you need reset your volatile dependencies\n')
    ensure_dir(VENDOR)

    for mod, uri in mod_map.items():
        path = Path(VENDOR / repo_dir(uri))
        mark = '[created]' if path.exists() else ''
        print(f'Git module: {mod} (at {path} {mark})')

        try:
            print('\nTrying to clone repository')
            with chdir(VENDOR):
                run(f'git clone {uri} {path} --depth=1')
        except RuntimeError:
            print('\nUpdating repository')
            with chdir(path):
                run('git checkout master')
                run('git pull --rebase origin master')

        if not find_spec(mod):
            with chdir(path):
                run(f'{python} setup.py develop')


if __name__ == '__main__':
    main()
