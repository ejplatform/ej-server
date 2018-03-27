from invoke import task


@task
def sass(ctx, watch=False):
    watch = ' --watch' if watch else ''
    ctx.run('sass lib/scss/main.scss:lib/assets/css/main.css' + watch, pty=True)


@task
def run(ctx, no_toolbar=False, postgres=False):
    env = {} if postgres else {'USE_SQLITE': 'true'}
    if no_toolbar:
        env['DISABLE_DJANGO_DEBUG_TOOLBAR'] = 'true'
    ctx.run('python manage.py runserver', pty=True, env=env)


@task
def db(ctx, migrate_only=False, postgres=False):
    env = {} if postgres else {'USE_SQLITE': 'true'}

    if not migrate_only:
        ctx.run('python manage.py makemigrations', pty=True, env=env)
    ctx.run('python manage.py migrate', pty=True, env=env)
