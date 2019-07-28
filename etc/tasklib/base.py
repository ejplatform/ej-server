import os
import sys
from pathlib import Path

python = sys.executable
directory = Path(os.path.dirname(__file__)).parent.parent
sys.path.append("src")
HELP_MESSAGES = {
    "dry-run": "Display docker commands on the screen without running them",
    "theme": "Set theme (e.g. cpa or default)",
    "watch": "Re-run when any file changes",
    "minify": "Minify resulting assets",
    "background": "Runs on background",
    "rocket": "Enable Rocket.Chat",
}


#
# Utility functions
#
def manage(ctx, cmd, *args, env=None, **kwargs):
    kwargs = {k.replace("_", "-"): v for k, v in kwargs.items() if v is not False}
    opts = " ".join(f'--{k} {"" if v is True else v}' for k, v in kwargs.items())
    opts = " ".join((*args, opts))
    cmd = f"{python} manage.py {cmd} {opts}"
    env = {**os.environ, **(env or {})}
    path = env.get("PYTHONPATH", ":".join(sys.path))
    env.setdefault("PYTHONPATH", f"src:{path}")
    os.chdir(str(directory))
    ctx.run(cmd, pty=True, env=env)


def su_docker(cmd):
    if os.getuid() == 0:
        return cmd
    else:
        return f"sudo {cmd}"


def runner(ctx, dry_run, **extra):
    def do(cmd, **kwargs):
        if dry_run:
            print(cmd)
        else:
            kwargs = dict(extra, **kwargs)
            return ctx.run(cmd, **kwargs)

    return do


def docker_deploy_variables(path):
    ns = {}
    seq = (list, tuple)
    to_str = lambda x: ",".join(map(str, x)) if isinstance(x, seq) else str(x)
    with open(path) as fd:
        src = fd.read()
        exec(src, ns)
    return {k: to_str(v) for k, v in ns.items() if k.isupper()}


def set_theme(theme):
    if theme and "/" in theme:
        theme = theme.rstrip("/")
        root = f"{theme}/"
        theme = os.path.basename(theme)
    elif theme and theme != "default":
        root = f"lib/themes/{theme}/"
    elif "EJ_THEME" in os.environ:
        theme = os.environ["EJ_THEME"]
        root = "lib/" if theme == "default" else f"lib/themes/{theme}/"
    else:
        theme = "default"
        root = "lib/"

    os.environ["EJ_THEME"] = theme
    return theme, root


def watch_path(path, func, poll_time=0.5, name=None, skip_first=False):
    """
    Watch path and execute the given function everytime a file changes.
    """
    import time
    from watchdog.observers import Observer
    from watchdog.events import (
        FileSystemEventHandler,
        FileCreatedEvent,
        FileDeletedEvent,
        FileModifiedEvent,
        FileMovedEvent,
    )

    file_event = (FileCreatedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent)
    last = time.time()

    def dispatch(ev):
        nonlocal last

        if (
            ev.src_path.endswith("__")
            or ev.src_path.startswith("__")
            or ev.src_path.startswith("~")
            or ev.src_path.startswith(".")
        ):
            return

        if isinstance(ev, file_event):
            last = start = time.time()
            time.sleep(poll_time)
            if last == start:
                print(f"File modified: {ev.src_path}")
                func()

    observer = Observer()
    handler = FileSystemEventHandler()
    handler.dispatch = dispatch
    observer.schedule(handler, path, recursive=True)
    observer.start()
    name = name or func.__name__
    print(f"Running {name} in watch mode.")
    if not skip_first:
        func()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def exec_watch(path, func, name, watch=False, background=False, poll_time=0.5):
    path = str(path)
    if watch and background:
        go = lambda: watch_path(path, func, name=name, poll_time=poll_time)
        return exec_watch(path, go, name, background=True)
    elif watch:
        return watch_path(path, func, name=name, poll_time=poll_time)
    elif background:
        from threading import Thread

        def go():
            print(".", end="", flush=True)
            try:
                func()
            except KeyboardInterrupt:
                pass

        thread = Thread(target=go, daemon=True)
        thread.start()
    else:
        func()
