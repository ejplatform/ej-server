import os

from invoke import task

from .base import manage, set_theme, directory

__all__ = ["db", "db_fake", "db_reset"]


@task
def db(ctx, migrate_only=False):
    """
    Perform migrations
    """
    if not migrate_only:
        manage(ctx, "makemigrations")
    manage(ctx, "migrate")


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
