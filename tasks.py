import os
import pathlib
import sys

from invoke import task

python = sys.executable
sys.path.append('src')


#
# Call python manage.py in a more robust way
#
def manage(ctx, cmd, env=None, **kwargs):
    kwargs = {k.replace('_', '-'): v for k, v in kwargs.items() if v is not False}
    opts = ' '.join(f'--{k} {"" if v is True else v}' for k, v in kwargs.items())
    cmd = f'{python} manage.py {cmd} {opts}'
    env = dict(env or {})
    env.setdefault('PYTHONPATH', f'src:{env.get("PYTHONPATH", "")}')
    print(f'Run: {cmd}')
    ctx.run(cmd, pty=True, env=env)


@task
def sass(ctx, no_watch=False, trace=False, theme=None):
    """
    Run Sass compiler
    """

    cmd_main = 'lib/scss/maindefault.scss:lib/assets/css/maindefault.css'
    cmd_rocket = 'lib/scss/rocket.scss:lib/assets/css/rocket.css'

    themes_path = 'lib/themes'
    cmd_themes = ''
    for theme in os.listdir(themes_path):
        cmd_themes += themes_path  + '/' + theme + f"/scss/main.scss:lib/assets/css/main{theme}.css "
        os.symlink('../themes/' + theme + '/assets' , 'lib/assets/' + theme) 

    suffix = '' if no_watch else ' --watch'
    suffix += ' --trace' if trace else ''

    ctx.run('rm .sass-cache -rf')
    cmd = (f'sass {cmd_main} {cmd_rocket} {cmd_themes} {suffix}')

    print('Running:', cmd)
    ctx.run(cmd, pty=True)


@task
def js(ctx):
    """
    Build js assets
    """
    print('Nothing to do now ;)')


@task
def run(ctx, no_toolbar=False, gunicorn=False, migrate=False,
        ask_input=False, assets=False):
    """
    Run development server
    """
    env = {}
    if no_toolbar:
        env['DISABLE_DJANGO_DEBUG_TOOLBAR'] = 'true'

    if migrate:
        no_input = not ask_input
        manage(ctx, 'migrate', noinput=no_input)

    if assets:
        # Populate db with assets
        db_assets(ctx)

    if gunicorn:
        from gunicorn.app.wsgiapp import run as run_gunicorn

        env['PATH'] = os.environ['PATH']
        env['PYTHONPATH'] = 'src'
        args = [
            # '-m', 'gunicorn.app.wsgiapp',
            'ej.wsgi', '-w', '4', '-b', '0.0.0.0:5000',
            '--error-logfile=-',
            '--access-logfile=-',
            '--log-level', 'info',
        ]

        # Fixme, use execle to replace the current process
        # print('Running: gunicorn', ' '.join(args))
        # os.execle(python, *args, env)
        sys.argv = ['gunicorn', *args]
        run_gunicorn()
    else:
        manage(ctx, 'runserver 0.0.0.0:8000', env=env)


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
def db_reset(ctx):
    """
    Reset data in database and optionally fill with fake data
    """
    ctx.run('rm -f local/db/db.sqlite3')
    manage(ctx, 'migrate')


@task
def db_fake(ctx, users=True, conversations=True, admin=True, safe=False):
    """
    Adds fake data to the database
    """
    msg_error = 'Release build. No fake data will be created!'

    if safe:
        if os.environ.get("FAKE_DB") == 'true':
            print('Creating fake data...')
        else:
            return print(msg_error)
    if users:
        manage(ctx, 'createfakeusers', admin=admin)
    if conversations:
        manage(ctx, 'createfakeconversations')


@task
def db_assets(ctx, path=None, force=False):
    """
    Install assets from a local folder in the database.
    """

    resources = pathlib.Path('lib/resources')
    pages = resources / 'pages'
    fragments = resources / 'fragments'
    data = resources / 'data'

    if path is not None:
        path = pathlib.Path(path)
        if (path / 'pages').exists():
            pages = path / 'pages'
        if (path / 'fragments').exists():
            pages = path / 'fragments'
        if (path / 'data').exists():
            pages = path / 'data'

    icons = data / 'social-icons.json'
    manage(ctx, 'loadpages', path=pages, force=force)
    manage(ctx, 'loadfragments', path=fragments, force=force)
    manage(ctx, 'loadsocialmediaicons', path=icons, force=force)


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
def i18n(ctx, compile=False, edit=False, lang='pt_BR', keep_pot=False):
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
        ctx.run('pybabel extract -F etc/babel.cfg -o locale/jinja2.pot .')

        print('Join Django + Jinja translation files')
        ctx.run('msgcat locale/django.pot locale/jinja2.pot --use-first -o locale/join.pot', pty=True)
        ctx.run(r'''sed -i '/"Language: \\n"/d' locale/join.pot''', pty=True)

        print(f'Update locale {lang} with Jinja2 messages')
        ctx.run(f'msgmerge locale/{lang}/LC_MESSAGES/django.po locale/join.pot -U')

        if not keep_pot:
            print('Cleaning up')
            ctx.run('rm locale/*.pot')


#
# Good practices and productivity
#
@task
def install_hooks(ctx):
    """
    Install git hooks in repository.
    """
    print('Installing flake8 pre-commit hook')
    ctx.run('flake8 --install-hook=git')


@task
def update_deps(ctx, all=False, reset=False):
    """
    Update volatile dependencies
    """
    if reset:
        ctx.run('rm -fr local/vendor/')
    ctx.run(f'{python} etc/scripts/install-deps.py')
    if all:
        ctx.run(f'{python} -m pip install -r etc/requirements/develop.txt')
    else:
        print('By default we only update the volatile dependencies. Run '
              '"inv update-deps --all" in order to update everything.')


@task
def configure(ctx, silent=False):
    """
    Install dependencies and configure a test server.
    """
    if silent:
        ask = lambda x: print(x + 'yes') or True
    else:
        ask = lambda x: input(x + ' (y/n) ').lower() == 'y'

    print('\nLoading dependencies (inv update-deps)')
    update_deps(ctx, all=True)

    print('\nCreating database and running migrations (inv db)')
    db(ctx)

    if ask('\nLoad assets to database?'):
        print('Running inv db-assets')
        db_assets(ctx)

    if ask('\nLoad fake data to database?'):
        print('Running inv db-fake')
        db_fake(ctx)


#
# Prepare deploy
#
@task
def prepare_deploy(ctx, ask_input=False):
    """
    Deploy checklist:

    * Build CSS assets
    * Build JS assets
    * Compile translations
    * Collect static files
    * Save assets to database
    """
    no_input = not ask_input

    # CSS
    sass(ctx, no_watch=no_input)

    # Js
    js(ctx)

    # Translations
    i18n(ctx, compile=no_input)

    # Static files
    manage(ctx, 'collectstatic', noinput=no_input)
