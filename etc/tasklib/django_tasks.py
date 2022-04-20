import os
import sys

from invoke import task

from .base import set_theme, manage, directory

__all__ = ["clean_migrations", "collect", "gunicorn", "manage_", "notebook", "run", "shell"]


@task
def clean_migrations(_ctx, all=False, yes=False):
    """
    Remove all automatically created migrations.
    """
    import re

    auto_migration = re.compile(r"\d{4}_auto_\w+.py")
    all_migration = re.compile(r"\d{4}\w+.py")

    remove_files = []
    for app in os.listdir("src"):
        migrations_path = f"src/{app}/migrations/"
        if os.path.exists(migrations_path):
            migrations = os.listdir(migrations_path)
            if "__pycache__" in migrations:
                migrations.remove("__pycache__")
            if all:
                remove_files.extend(
                    [f"{migrations_path}{f}" for f in migrations if all_migration.fullmatch(f)]
                )
            elif sorted(migrations) == ["__init__.py", "0001_initial.py"]:
                remove_files.append(f"{migrations_path}/0001_initial.py")
            else:
                remove_files.extend(
                    [f"{migrations_path}/{f}" for f in migrations if auto_migration.fullmatch(f)]
                )

    print("Listing auto migrations")
    for file in remove_files:
        print(f"* {file}")
    if all:
        print("REMOVING ALL MIGRATIONS IS DANGEROUS AND SHOULD ONLY BE " "USED IN TESTING")
    if yes or input("Remove those files? (y/N)").lower() == "y":
        for file in remove_files:
            os.remove(file)


@task
def collect(ctx, theme=None):
    """
    Runs Django's collectstatic command
    """
    theme, root = set_theme(theme)
    root_css = directory / "lib/build/css/"
    root_js = directory / "lib/build/js/"

    # Select the correct minified build for CSS assets
    for file in ["main", "hicontrast"]:
        from_path = root_css / (file + f"-{theme}.min.css")
        to_path = root_css / (file + ".css")
        if not from_path.exists():
            print('Please run "inv build-assets" first!', file=sys.stderr)
        with open(to_path, "w") as fd:
            fd.write(open(from_path).read())

    # Select minified javascript assets
    for file in os.listdir(str(root_js)):
        if file.endswith(".min.js"):
            from_path = root_js / file
            to_path = root_js / (file[:-6] + "js")
            if not from_path.exists():
                print('Please run "inv build-assets" first!', file=sys.stderr)
            with open(to_path, "w") as fd:
                fd.write(open(from_path).read())

    manage(ctx, "collectstatic --noinput")


@task
def gunicorn(_ctx, debug=None, environment="production", port=8000, workers=0, theme=None):
    """
    Run application using gunicorn for production deploys.

    It assumes that static media is served by a reverse proxy.
    """

    from gunicorn.app.wsgiapp import run as run_gunicorn

    theme, _ = set_theme(theme)
    workers = workers or os.cpu_count() or 1

    env = {
        "DISABLE_DJANGO_DEBUG_TOOLBAR": str(not debug),
        "PYTHONPATH": "src",
        "DJANGO_ENVIRONMENT": environment,
        "EJ_THEME": theme,
    }
    if debug is not None:
        env["DJANGO_DEBUG"] = str(debug).lower()
    os.environ.update(env)
    args = [
        "--timeout=120",
        "ej.wsgi",
        "-w",
        str(workers),
        "-b",
        f"0.0.0.0:{port}",
        "--error-logfile=-",
        "--access-logfile=-",
        "--log-level",
        "info",
        f"--pythonpath={directory}/src",
    ]
    sys.argv = ["gunicorn", *args]
    run_gunicorn()


@task(name="manage")
def manage_(ctx, command, noinput=False, args=""):
    """
    Run a Django manage.py command
    """
    kwargs = {}
    if noinput:
        kwargs["noinput"] = noinput
    manage(ctx, f"{command} {args}", **kwargs)


@task
def notebook(ctx):
    """
    Start a notebook server.
    """

    db_path = os.path.abspath(directory / "local" / "db" / "db.sqlite3")
    ctx.run(
        "jupyter-notebook",
        env={
            "PYTHONPATH": directory / "src",
            "DJANGO_SETTINGS_MODULE": "ej.settings",
            "DJANGO_DB_URL": f"sqlite:///{db_path}",
        },
    )


@task
def run(ctx, no_toolbar=False, theme=None):
    """
    Run development server
    """
    set_theme(theme)
    env = {"DISABLE_DJANGO_DEBUG_TOOLBAR": "true" if no_toolbar else "false"}
    manage(ctx, "runserver 0.0.0.0:8000", env=env)


@task
def shell(ctx):
    """
    Starts a Django shell
    """
    manage(ctx, "shell")
