from invoke import task


@task
def sass(ctx, no_watch=False, trace=False):
    """
    Run Sass compiler
    """
    suffix = '' if no_watch else ' --watch'
    suffix += ' --trace' if trace else ''
    ctx.run('sass lib/scss/main.scss:lib/assets/css/main.css' + suffix, pty=True)


@task
def run(ctx, no_toolbar=False):
    """
    Run development server
    """
    env = {}
    if no_toolbar:
        env['DISABLE_DJANGO_DEBUG_TOOLBAR'] = 'true'
    ctx.run('python manage.py runserver', pty=True, env=env)


@task
def db(ctx, migrate_only=False):
    """
    Perform migrations
    """
    if not migrate_only:
        ctx.run('python manage.py makemigrations', pty=True)
    ctx.run('python manage.py migrate', pty=True)


@task
def db_reset(ctx, fake=False, postgres=False):
    """
    Reset data in database and optionally fill with fake data
    """
    ctx.run('rm db.sqlite3 -f')
    ctx.run('python manage.py migrate', pty=True)
    if fake:
        db_fake(ctx, postgres=postgres)


@task
def db_fake(ctx, no_users=False, no_conversations=False, no_admin=False):
    """
    Adds fake data to the database
    """
    if not no_users:
        suffix = '' if no_admin else ' --admin'
        ctx.run('python manage.py createfakeusers' + suffix, pty=True)
    if not no_conversations:
        ctx.run('python manage.py createfakeconversations', pty=True)
