import os
import pathlib
import sys

from invoke import task

python = sys.executable


#
# Call python manage.py in a more robust way
#
def manage(ctx, cmd, env=None, **kwargs):
    kwargs = {k.replace('_', '-'): v for k, v in kwargs.items() if v is not False}
    opts = ' '.join(f'--{k} {"" if v is True else v}' for k, v in kwargs.items())
    cmd = f'{python} manage.py {cmd} {opts}'
    print(f'Run: {cmd}')
    ctx.run(cmd, pty=True, env=(env or {}))


@task
def sass(ctx, no_watch=False, trace=False):
    """
    Run Sass compiler
    """
    suffix = '' if no_watch else ' --watch'
    suffix += ' --trace' if trace else ''
    ctx.run('rm .sass-cache -rf')
    ctx.run('sass lib/scss/main.scss:lib/assets/css/main.css lib/scss/rocket.scss:lib/assets/css/rocket.css' + suffix,
            pty=True)


@task
def run(ctx, no_toolbar=False):
    """
    Run development server
    """
    env = {}
    if no_toolbar:
        env['DISABLE_DJANGO_DEBUG_TOOLBAR'] = 'true'
    manage(ctx, 'runserver')


#
# Db tasks
#
@task
def db(ctx, migrate_only=False):
    """
    Perform migrations
    """
    if not migrate_only:
        manage(ctx, 'makemigrations')
    manage(ctx, 'migrate')


@task
def db_reset(ctx, fake=False, no_assets=False):
    """
    Reset data in database and optionally fill with fake data
    """
    ctx.run('rm db.sqlite3 -f')
    manage(ctx, 'migrate')
    if fake:
        db_fake(ctx)
    if not no_assets:
        db_assets(ctx)


@task
def db_fake(ctx, no_users=False, no_conversations=False, no_admin=False, safe=False):
    """
    Adds fake data to the database
    """
    buildfile = 'local/build.info'
    msg_error = 'Release build. No fake data will be created!'

    if safe:
        if os.path.exists(buildfile):
            with open(buildfile) as F:
                data = F.read()
                print(f'Found build file at {buildfile}: {data}')

            if data.startswith('develop'):
                print('Creating fake data...')
            else:
                return print(msg_error)
        else:
            return print(msg_error)

    if not no_users:
        manage(ctx, 'createfakeusers', admin=not no_admin)
    if not no_conversations:
        manage(ctx, 'createfakeconversations')
        manage(ctx, 'loadpages', path='local-example/pages/')


@task
def db_assets(ctx, path=None, force=False):
    """
    Install assets from a local folder in the database.
    """

    if path is None:
        path = 'local' if os.path.exists('local') else 'local-example'
    base = pathlib.Path(path)
    manage(ctx, 'loadpages', path=base / 'pages', force=force)
    manage(ctx, 'loadfragments', path=base / 'fragments', force=force)
    manage(ctx, 'loadsocialmediaicons', path=base / 'social-icons.json', force=force)


#
# Docker
#
@task
def docker_clean(ctx, no_sudo=False, all=False, volumes=False, networks=False, images=False, containers=False):
    """
    Clean unused docker resources.
    """

    docker = 'docker' if no_sudo else 'sudo docker'
    run = lambda cmd: ctx.run(cmd, pty=True)
    if volumes or all:
        run(f'{docker} volume rm $({docker} volume ls -qf dangling=true)')
    if networks or all:
        run(f'{docker} network rm $({docker} network ls | grep "bridge" | awk \'/ / {" print $1 "}\')')
    if images or all:
        run(f'{docker} rmi $({docker} images --filter "dangling=true" -q --no-trunc)')
    if containers or all:
        run(f'{docker} rm $({docker} ps -qa --no-trunc --filter "status=exited")')

    if not any([all, volumes, networks, images, containers]):
        print('You must select one kind of docker resource to clean.', file=sys.stderr)


#
# Translations
#
@task
def i18n(ctx, compile=False, edit=False, lang='pt_BR'):
    """
    Extract messages for translation.
    """
    if edit:
        ctx.run(f'poedit locale/{lang}/LC_MESSAGES/django.po')
    elif compile:
        manage(ctx, 'compilemessages')
    else:
        print('Collecting messages')
        manage(ctx, 'makemessages', all=True, keep_pot=True)

        print('Extract Jinja translations')
        ctx.run('pybabel extract -F babel.cfg -o locale/jinja2.pot .')

        print('Join Django + Jinja translation files')
        ctx.run('msgcat locale/django.pot locale/jinja2.pot --use-first -o locale/join.pot', pty=True)
        ctx.run(r'''sed -i '/"Language: \\n"/d' locale/join.pot''', pty=True)

        print(f'Update locale {lang} with Jinja2 messages')
        ctx.run(f'msgmerge locale/{lang}/LC_MESSAGES/django.po locale/join.pot -U')

        print('Cleaning up')
        ctx.run('rm locale/*.pot')
