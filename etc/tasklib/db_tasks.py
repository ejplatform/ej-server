import os

from invoke import task

from .base import manage, set_theme, directory

__all__ = ["db", "db_assets", "db_fake", "db_reset"]


@task
def db(ctx, migrate_only=False):
    """
    Perform migrations
    """
    if not migrate_only:
        manage(ctx, "makemigrations")
    manage(ctx, "migrate")


@task
def db_assets(ctx, force=False, theme=None):
    """
    Install assets from a local folder in the database.
    """
    theme, root = set_theme(theme)
    resources = directory / "lib/resources"
    pages = [resources / "pages"]
    fragments = [resources / "fragments"]
    icons = [resources / "data/social-icons.json"]

    if theme != "default":
        print(f"Building assets for the {theme} theme...")

        path = root / "resources"
        if (path / "pages").exists():
            pages.insert(0, path / "pages")
        if (path / "fragments").exists():
            fragments.insert(0, path / "fragments")
        if (path / "data").exists():
            icons.insert(0, path / "data/social-icons.json")

    # In forced mode, process the generic assets first, then insert the specific
    # ones.
    if force:
        for lst in [pages, fragments, icons]:
            lst.reverse()

    # Load assets from Django commands
    for path in pages:
        manage(ctx, "loadpages", path=path, force=force)
    # for path in fragments:
    #    manage(ctx, 'loadfragments', path=path, force=force)
    # for path in icons:
    #    manage(ctx, 'loadsocialmediaicons', path=path, force=force)


@task
def db_fake(
    ctx, users=True, conversations=True, admin=True, user=True, safe=False, theme=None, clusters=True
):
    """
    Adds fake data to the database
    """
    set_theme(theme)
    msg_error = "Release build. No fake data will be created!"

    if safe:
        if os.environ.get("FAKE_DB") == "true":
            print("Creating fake data...")
        else:
            return print(msg_error)
    if users:
        manage(ctx, "createfakeusers", admin=admin, user=user)
    if conversations:
        manage(ctx, "createfakeconversations")
    if clusters:
        manage(ctx, "createfakeclusters")


@task
def db_reset(ctx):
    """
    Reset data in database and optionally fill with fake data
    """
    ctx.run("rm -f local/db/db.sqlite3")
    manage(ctx, "migrate")
