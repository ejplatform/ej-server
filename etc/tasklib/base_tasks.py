import os

from invoke import task

from .base import python
from .build_tasks import requirements, docs, i18n, sass, js
from .db_tasks import db, db_fake, db_assets

__all__ = ["bash", "configure"]


@task
def bash(_ctx):
    """
    Starts a bash shell.
    """
    print("\nStarting bash console")
    os.execve("/bin/bash", ["bash"], os.environ)


@task
def configure(ctx, silent=False, dev=True):
    """
    Install dependencies and configure a test server.
    """
    if silent:
        ask = lambda x: print(x + "yes") or True
    else:
        ask = lambda x: input(x + " (y/n) ")[0].lower() == "y"

    # Update requirements
    requirements(ctx)

    if ask("\nInstall dependencies?"):
        suffix = " -r etc/requirements-dev.txt" if dev else ""
        ctx.run(f"{python} -m pip install markupsafe toolz")
        ctx.run(f"{python} -m pip install sidekick")
        ctx.run(f"{python} -m pip install -r etc/requirements.txt" + suffix)

    if ask("\nInstall js dependencies?"):
        cwd = os.getcwd()
        os.chdir(cwd + "/lib")
        try:
            ctx.run("npm install")
        finally:
            os.chdir(cwd)

    if ask("\nInitialize database (inv db)?"):
        db(ctx)
        if ask("\nLoad assets to database (inv db-assets)?"):
            db_assets(ctx)
        if ask("\nLoad fake data to database (inv db-fake)?"):
            db_fake(ctx)

    for msg, action, kwargs in [
        ("Compile js assets? (inv js)?", js, {}),
        ("Compile CSS resources (inv sass)?", sass, {}),
        ("Compile translations (inv i18n -c)?", i18n, {"compile": True}),
        ("Build documentation (inv docs)?", docs, {}),
    ]:
        if ask("\n" + msg):
            action(ctx, **kwargs)
