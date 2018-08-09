import json
import os
import pathlib
import sys
from test.test_bdb import dry_run

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
    exec(ctx, cmd, pty=True, env=env)


#
# Build assets
#
@task
def sass(ctx, watch=True, theme=None, trace=False, dry_run=False):
    """
    Run Sass compiler
    """

    go = runner(ctx, dry_run, pty=True)
    cmd = 'sass'
    cmd += ' lib/scss/maindefault.scss:lib/assets/css/maindefault.css'
    cmd += ' lib/scss/maindefault.scss:lib/assets/css/main.css'
    cmd += ' lib/scss/rocket.scss:lib/assets/css/rocket.css'

    # Handle themes
    themes_path = 'lib/themes'
    for theme in os.listdir(themes_path):
        cmd += f' lib/themes/{theme}/scss/main.scss:lib/assets/css/main{theme}.css'
        asset_dir = f'lib/assets/{theme}'
        if os.path.exists(asset_dir):
            os.remove(asset_dir)
        os.symlink(f'../themes/{theme}/assets/', asset_dir)

    cmd += ' --watch' if watch else ''
    cmd += ' --trace' if trace else ''
    go('rm -rf .sass-cache')
    go(cmd)


@task
def js(ctx):
    """
    Build js assets
    """
    print('Nothing to do now ;)')


#
# Django tasks
#
@task
def run(ctx, no_toolbar=False):
    """
    Run development server
    """
    env = {}
    if no_toolbar:
        env['DISABLE_DJANGO_DEBUG_TOOLBAR'] = 'true'
    else:
        manage(ctx, 'runserver 0.0.0.0:8000', env=env)


@task
def run_deploy(ctx, debug=False, environment='production', port=5000, workers=4):
    """
    Run application using gunicorn for production deploys.

    It assumes that static media is served by a reverse proxy such as nginx.
    """

    from gunicorn.app.wsgiapp import run as run_gunicorn

    env = {
        'DISABLE_DJANGO_DEBUG_TOOLBAR': str(not debug),
        'PYTHONPATH': 'src',
        # 'DJANGO_ENVIRONMENT': environment,
        # 'DJANGO_DEBUG': str(debug),
    }
    os.environ.update(env)

    args = [
        'ej.wsgi', '-w', str(workers), '-b', f'0.0.0.0:{port}',
        '--error-logfile=-',
        '--access-logfile=-',
        '--log-level', 'info',
    ]

    sys.argv = ['gunicorn', *args]
    run_gunicorn()


@task
def clean_migrations(ctx):
    """
    Remove all automatically created migrations.
    """
    import re
    auto_migration = re.compile(r'\d{4}_auto_\w+.py')

    remove_files = []
    for app in os.listdir('src'):
        migrations_path = f'src/{app}/migrations/'
        if os.path.exists(migrations_path):
            migrations = os.listdir(migrations_path)
            if '__pycache__' in migrations:
                migrations.remove('__pycache__')
            if sorted(migrations) == ['__init__.py', '0001_initial.py']:
                remove_files.append(f'{migrations_path}/0001_initial.py')
            else:
                remove_files.extend([
                    f'{migrations_path}/{f}' for f in migrations
                    if auto_migration.fullmatch(f)
                ])

    print('Listing auto migrations')
    for file in remove_files:
        print(f'* {file}')
    if input('Remove those files? (y/N)').lower() == 'n':
        for file in remove_files:
            os.remove(file)


#
# DB management
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
def dockerfiles_cmd(ctx, cmd, tag='latest', dry_run=False, org='ejplatform',
                    args_web='', args_nginx='', args_dev=''):
    cmd = su_docker(f'docker {cmd} -f docker/Dockerfile')
    do = runner(ctx, dry_run, pty=True)
    do(f'{cmd}       -t {org}/web:{tag}   {args_web}')
    do(f'{cmd}-dev   -t {org}/dev:{tag}   {args_dev}')
    do(f'{cmd}-nginx -t {org}/nginx:{tag} {args_nginx}')


@task
def docker_build(ctx, tag='latest', theme='default:ejplatform', extra_args='',
                 dry_run=False, cache=False):
    """
    Rebuild all docker images for the project.
    """
    for item in theme.split(','):
        theme, org = item.split(':') if ':' in item else (item, item)
        base_image = f'{org}/web:{tag}'
        args = f'{extra_args} --build-arg THEME={theme}'
        child_args = f'{args} --build-arg BASE_IMAGE={base_image}'
        cache_web = cache_nginx = cache_dev = ''
        if cache:
            cache_web = f'--cache-from {org}/web:{tag} '
            cache_dev = f'--cache-from {org}/dev:{tag} '
            cache_nginx = f'--cache-from {org}/nginx:{tag} '
        kwargs = {
            'args_web': cache_web + args,
            'args_dev': cache_dev + child_args,
            'args_nginx': cache_nginx + child_args,
        }
        dockerfiles_cmd(ctx, 'build .', tag=tag, dry_run=dry_run, org=org, **kwargs)


@task
def docker_push(ctx, tag='latest', theme='default:ejplatform', extra_args='',
                dry_run=False):
    """
    Rebuild all docker images for the project.
    """
    cmd = su_docker(f'docker push')
    do = runner(ctx, dry_run, pty=True)

    for item in theme.split(','):
        theme, org = item.split(':') if ':' in item else (item, item)
        do(f'{cmd} {org}/web:{tag}   {extra_args}')
        do(f'{cmd} {org}/nginx:{tag} {extra_args}')
        do(f'{cmd} {org}/dev:{tag}   {extra_args}')


@task
def docker_pull(ctx, tag='latest', theme='default:ejplatform', extra_args='',
                dry_run=False):
    """
    Rebuild all docker images for the project.
    """
    cmd = su_docker(f'docker pull')
    do = runner(ctx, dry_run, pty=True)

    for item in theme.split(','):
        theme, org = item.split(':') if ':' in item else (item, item)
        do(f'{cmd} {org}/web:{tag}   {extra_args}')
        do(f'{cmd} {org}/nginx:{tag} {extra_args}')
        do(f'{cmd} {org}/dev:{tag}   {extra_args}')


@task
def docker_run(ctx, env, cmd=None, port=8000, clean_perms=False, deploy=False,
               compose_file=None, dry_run=False, tag='latest'):
    """
    Runs EJ platform using a docker container.

    Use inv docker-run <cmd>, where cmd is one of single, start, up, run,
    deploy.
    """
    docker = su_docker('docker')
    do = runner(ctx, dry_run, pty=True)
    if compose_file is None and deploy or env == 'deploy':
        compose_file = 'docker/docker-compose.deploy.yml'
    elif compose_file is None:
        compose_file = 'docker/docker-compose.yml'
    compose = f'{docker}-compose -f {compose_file}'

    if env == 'single':
        do(f'{docker} run '
           f'-v `pwd`:/app '
           f'-p {port}:8000 '
           f'-it ejplatform/dev:{tag} {cmd or "run"}')
    elif env == 'start':
        do(f'{compose} up -d')
        do(f'{compose} run -p {port}:8000 web {cmd or "bash"}')
        do(f'{compose} stop')
    elif env == 'up':
        do(f'{compose} up')
    elif env == 'run':
        do(f'{compose} run -p {port}:8000 web {cmd or "bash"}')
    elif env == 'deploy':
        do(f'{compose} up')
    else:
        raise SystemExit(f'invalid choice for env: {env}\n'
                         f'valid options: single, start, up, run, deploy')
    if clean_perms:
        do(f'sudo chown `whoami`:`whoami` * -R')


@task
def docker_clean(ctx, no_sudo=False, all=False, volumes=False, networks=False, images=False, containers=False,
                 force=False):
    """
    Clean unused docker resources.
    """

    docker = 'docker' if no_sudo else 'sudo docker'
    force = ' --force ' if force else ''
    do = runner(ctx, dry_run, pty=True)
    if volumes or all:
        do(f'{docker} volume rm {force} $({docker} volume ls -q dangling=true)')
    if networks or all:
        do(f'{docker} network rm {force} $({docker} network ls | grep "bridge" | awk \'/ / {" print $1 "}\')')
    if images or all:
        do(f'{docker} rmi {force} $({docker} images --filter "dangling=true" -q --no-trunc)')
    if containers or all:
        do(f'{docker} rm {force} $({docker} ps -qa --no-trunc --filter "status=exited")')

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
        ctx.run(f'{python} etc/scripts/compilemessages.py')
    else:
        print('Collecting messages')
        manage(ctx, 'makemessages', all=True, keep_pot=True)

        print('Extract Jinja translations')
        exec(ctx, 'pybabel extract -F etc/babel.cfg -o locale/jinja2.pot .')

        print('Join Django + Jinja translation files')
        exec(ctx, 'msgcat locale/django.pot locale/jinja2.pot --use-first -o locale/join.pot', pty=True)
        exec(ctx, r'''sed -i '/"Language: \\n"/d' locale/join.pot''', pty=True)

        print(f'Update locale {lang} with Jinja2 messages')
        ctx.run(f'msgmerge locale/{lang}/LC_MESSAGES/django.po locale/join.pot -U')

        if not keep_pot:
            print('Cleaning up')
            ctx.run('rm locale/*.pot')


#
# Good practices and productivity
#
@task
def lint(ctx):
    """
    Execute linters
    """
    ctx.run('flake8 src/', pty=True)


@task
def install_hooks(ctx):
    """
    Install git hooks in repository.
    """
    print('Installing flake8 pre-commit hook')
    ctx.run('flake8 --install-hook=git')


@task
def update_deps(ctx, all=False):
    """
    Update volatile dependencies
    """
    ctx.run(f'{python} etc/scripts/install-deps.py')
    if all:
        exec(ctx, f'{python} -m pip install -r etc/requirements/local.txt')
        exec(ctx, f'{python} -m pip install -r etc/requirements/develop.txt')
    else:
        print('By default we only update the volatile dependencies. Run '
              '"inv update-deps --all" in order to update everything.')


@task
def configure(ctx, silent=False):
    """
    Install dependencies and configure a test server.
    """
    if silent:
        ask = (lambda x: print(x + 'yes') or True)
    else:
        ask = (lambda x: input(x + ' (y/n) ').lower() == 'y')

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
# Useful docker entry points
#
@task
def bash(ctx):
    """
    Starts a bash shell.
    """
    print('\nStarting bash console')
    os.execve('/bin/bash', ['bash'], os.environ)


@task
def shell(ctx):
    """
    Starts a Django shell
    """
    manage(ctx, 'shell')


@task
def test(ctx):
    """
    Run all unittests.
    """
    ctx.run('pytest')


#
# Deploy tasks
#
@task
def docker_deploy(ctx, cmd, environment='production', dry_run=False):
    """
    Start a deploy build for the platform.
    """
    json_file = 'local/deploy/config.json'
    env = deploy_variables(json.loads(json_file))
    compose = su_docker('docker-compose -f local/deploy/docker-compose.yml')
    do = runner(ctx, dry_run, pty=True, env=env)

    if cmd == 'build':
        do(f'{compose} build')

    elif cmd == 'run':
        pass

    elif cmd == 'publish':
        do(f'{compose} build')

    elif cmd == 'notify':
        do(f'{compose} build')

    else:
        raise SystemExit(f'invalid command: {cmd}\n'
                         f'Possible commands: build, run, publish, notify')


#
# Utilities
#
def exec(ctx, cmd, **kwargs):
    print(f'Running: {cmd}')
    ctx.run(cmd, **kwargs)


def su_docker(cmd):
    if os.getuid() == 0:
        return cmd
    else:
        return f'sudo {cmd}'


def runner(ctx, dry_run, **extra):
    def do(cmd, **kwargs):
        if dry_run:
            print(cmd)
        else:
            kwargs = dict(extra, **kwargs)
            return exec(ctx, cmd, **kwargs)

    return do


def deploy_variables(data):
    return {k.upper(): v for k, v in data.items()}
