import os
import pathlib
import sys
from pathlib import Path

from invoke import task

python = sys.executable
directory = Path(os.path.dirname(__file__))
sys.path.append('src')
HELP_MESSAGES = {
    'dry-run': 'Display docker commands on the screen without running them',
    'theme': 'Set theme (e.g. cpa or default)',
    'watch': 'Re-run when any file changes',
    'minify': 'Minify resulting assets',
    'background': 'Runs on background',
    'rocket': 'Enable Rocket.Chat',
}


#
# Call python manage.py in a more robust way
#
def manage(ctx, cmd, *args, env=None, **kwargs):
    kwargs = {k.replace('_', '-'): v for k, v in kwargs.items() if v is not False}
    opts = ' '.join(f'--{k} {"" if v is True else v}' for k, v in kwargs.items())
    opts = ' '.join((*args, opts))
    cmd = f'{python} manage.py {cmd} {opts}'
    env = {**os.environ, **(env or {})}
    path = env.get("PYTHONPATH", ":".join(sys.path))
    env.setdefault('PYTHONPATH', f'src:{path}')
    os.chdir(directory)
    ctx.run(cmd, pty=True, env=env, )


#
# Build assets
#
@task
def build_assets(ctx):
    """
    Builds all required assets to make EJ ready for deployment.
    """
    from toml import load

    config = load(open(directory / 'pyproject.toml'))

    # Build CSS
    for theme in config['tool']['ej']['conf']['themes']:
        print(f'\nBuilding theme: {theme!r}')
        sass(ctx, theme, suffix=f'-{theme}', minify=True)

    # Build Javascript
    print('Building javascript assets')
    js(ctx, minify=True)


@task(help={
    **HELP_MESSAGES,
    'suffix': 'Append suffix to resulting file names.',
})
def sass(ctx, theme=None, watch=False, background=False, suffix='', minify=False):
    """
    Run Sass compiler
    """

    theme, root = set_theme(theme)
    os.environ['EJ_THEME'] = theme or 'default'
    ctx.run(f'mkdir -p {directory / "lib/build/css"}')
    root = directory / f'{root}scss'
    minify = directory / 'lib/node_modules/.bin/minify'

    def go():
        import sass

        root_url = f'file://{directory / "lib/build/css/"}'
        for file in ('main', 'rocket', 'hicontrast'):
            try:
                css_path = directory / f'lib/build/css/{file}{suffix}.css'
                css_min_path = directory / f'lib/build/css/{file}{suffix}.min.css'
                map_path = directory / f'lib/build/css/{file}{suffix}.css.map'
                css, sourcemap = sass.compile(filename=str(root / f'{file}.scss'),
                                              source_map_filename=str(map_path),
                                              source_map_root=str(root_url),
                                              source_map_contents=True,
                                              source_map_embed=True,
                                              )
                with open(css_path, 'w') as fd:
                    fd.write(css)
                    if minify:
                        ctx.run(f'{minify} {css_path} > {css_min_path}')
                with open(map_path, 'w') as fd:
                    fd.write(sourcemap)

            except Exception as exc:
                print(f'ERROR EXECUTING SASS COMPILATION: {exc}')

    exec_watch(root, go, name='sass', watch=watch, background=background)
    print('Compilation finished!')


@task
def js(ctx, watch=False, minify=False):
    """
    Build js assets
    """
    build_cmd = 'npm run watch' if watch else 'npm run build'
    cwd = os.getcwd()
    try:
        path = Path(__file__).parent / 'lib'
        os.chdir(path)
        ctx.run('mkdir -p build/js/')
        ctx.run('rm build/js/main.js* -f')
        ctx.run(build_cmd)
        if minify:
            minify = directory / 'lib/node_modules/.bin/minify'
            base = directory / 'lib/build/js/'
            for path in os.listdir(base):
                if path.endswith('.js'):
                    path = str(base / path)
                    print(f'Minifying {path}')
                    ctx.run(f'{minify} {path} > {path[:-2]}.min.js')
    finally:
        os.chdir(cwd)


@task
def docs(ctx, orm=False):
    """
    Builds Sphinx documentation.
    """
    if orm:
        for app in ['ej_users', 'ej_profiles', 'ej_conversations', 'ej_boards',
                    'ej_clusters', 'ej_gamification', 'ej_dataviz',
                    'ej_rocketchat']:
            print(f'Making ORM graph for {app}')
            env = {'EJ_ROCKETCHAT_INTEGRATION': 'true'} if app == 'ej_rocketchat' else {}
            manage(ctx, 'graph_models', app, env=env, output=f'docs/dev-docs/orm/{app}.svg')
    else:
        print('call inv docs --orm to update ORM graphs')

    ctx.run('sphinx-build docs/ build/docs/', pty=True)


@task
def requirements(ctx):
    """
    Extract requirements.txt from Poetry file
    """
    import toml

    def extract_deps(deps):
        deps = deps.copy()
        deps.pop('python', None)
        lst = []

        for k, v in deps.items():
            if isinstance(v, str):
                version = v
                extra = ()
            else:
                version = v['version']
                extra = v.get('extras', ())

            if version[0] == '^':
                lst.append(f'{k} ~= {version[1:]}')
            else:
                lst.append(f'{k}{version}')
            for extra in extra:
                lst.append(f'{k}[{extra}]')
        return '\n'.join(lst)

    with open('pyproject.toml') as F:
        data = toml.load(F)
        deps = data['tool']['poetry']['dependencies']
        dev_deps = data['tool']['poetry']['dev-dependencies']

        with open('etc/requirements.txt', 'w') as F:
            F.write(extract_deps(deps))

        with open('etc/requirements-dev.txt', 'w') as F:
            F.write(extract_deps(dev_deps))


#
# Django tasks
#
@task
def run(ctx, no_toolbar=False, theme=None):
    """
    Run development server
    """
    set_theme(theme)
    env = {}
    if no_toolbar:
        env['DJANGO_DEBUG_TOOLBAR'] = 'disabled'
    manage(ctx, 'runserver 0.0.0.0:8000', env=env)


@task
def gunicorn(ctx, debug=None, environment='production', port=8000, workers=0, theme=None):
    """
    Run application using gunicorn for production deploys.

    It assumes that static media is served by a reverse proxy.
    """

    from gunicorn.app.wsgiapp import run as run_gunicorn
    theme, _ = set_theme(theme)
    workers = workers or os.cpu_count() or 1

    env = {
        'DISABLE_DJANGO_DEBUG_TOOLBAR': str(not debug),
        'PYTHONPATH': 'src',
        'DJANGO_ENVIRONMENT': environment,
        'EJ_THEME': theme,
    }
    if debug is not None:
        env['DJANGO_DEBUG'] = str(debug).lower()
    os.environ.update(env)
    args = [
        'ej.wsgi', '-w', str(workers), '-b', f'0.0.0.0:{port}',
        '--error-logfile=-',
        '--access-logfile=-',
        '--log-level', 'info',
        f'--pythonpath={directory}/src'
    ]
    sys.argv = ['gunicorn', *args]
    run_gunicorn()


@task
def clean_migrations(ctx, all=False, yes=False):
    """
    Remove all automatically created migrations.
    """
    import re
    auto_migration = re.compile(r'\d{4}_auto_\w+.py')
    all_migration = re.compile(r'\d{4}\w+.py')

    remove_files = []
    for app in os.listdir('src'):
        migrations_path = f'src/{app}/migrations/'
        if os.path.exists(migrations_path):
            migrations = os.listdir(migrations_path)
            if '__pycache__' in migrations:
                migrations.remove('__pycache__')
            if all:
                remove_files.extend([
                    f'{migrations_path}{f}' for f in migrations
                    if all_migration.fullmatch(f)
                ])
            elif sorted(migrations) == ['__init__.py', '0001_initial.py']:
                remove_files.append(f'{migrations_path}/0001_initial.py')
            else:
                remove_files.extend([
                    f'{migrations_path}/{f}' for f in migrations
                    if auto_migration.fullmatch(f)
                ])

    print('Listing auto migrations')
    for file in remove_files:
        print(f'* {file}')
    if all:
        print('REMOVING ALL MIGRATIONS IS DANGEROUS AND SHOULD ONLY BE '
              'USED IN TESTING')
    if yes or input('Remove those files? (y/N)').lower() == 'y':
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
def db_fake(ctx, users=True, conversations=True, admin=True, user=True, safe=False, theme=None, clusters=True):
    """
    Adds fake data to the database
    """
    set_theme(theme)
    msg_error = 'Release build. No fake data will be created!'

    if safe:
        if os.environ.get("FAKE_DB") == 'true':
            print('Creating fake data...')
        else:
            return print(msg_error)
    if users:
        manage(ctx, 'createfakeusers', admin=admin, user=user)
    if conversations:
        manage(ctx, 'createfakeconversations')
    if clusters:
        manage(ctx, 'createfakeclusters')


@task
def db_assets(ctx, force=False, theme=None):
    """
    Install assets from a local folder in the database.
    """
    theme, root = set_theme(theme)
    resources = pathlib.Path('lib/resources')
    pages = [resources / 'pages']
    fragments = [resources / 'fragments']
    icons = [resources / 'data/social-icons.json']

    if theme != 'default':
        print(f'Building assets for the {theme} theme...')

        path = pathlib.Path(root) / 'resources'
        if (path / 'pages').exists():
            pages.insert(0, path / 'pages')
        if (path / 'fragments').exists():
            fragments.insert(0, path / 'fragments')
        if (path / 'data').exists():
            icons.insert(0, path / 'data/social-icons.json')

    # In forced mode, process the generic assets first, then insert the specific
    # ones.
    if force:
        for lst in [pages, fragments, icons]:
            lst.reverse()

    # Load assets from Django commands
    for path in pages:
        manage(ctx, 'loadpages', path=path, force=force)
    # for path in fragments:
    #    manage(ctx, 'loadfragments', path=path, force=force)
    # for path in icons:
    #    manage(ctx, 'loadsocialmediaicons', path=path, force=force)


#
# Docker
#
@task(
    help={
        **HELP_MESSAGES,
        'task': 'One of "local", "single", "up", "down", "run", "exec" or "rocket"',
        'rocket': 'Enable Rocket.Chat',

    },
)
def docker(ctx, task, cmd=None, port=8000, file=None, dry_run=False,
           deploy=False, rocket=False, clean_perms=False):
    """
    Runs EJ platform using a docker container.
    """
    docker = su_docker('docker')
    do = runner(ctx, dry_run, pty=True)
    app = 'web' if deploy else 'app'

    if cmd == 'rocket':
        file = 'docker/docker-compose.rocket.yml'
    elif file is None and deploy:
        file = 'docker/docker-compose.deploy.yml'
    elif file is None:
        file = 'docker/docker-compose.local.yml'
    compose = f'{docker}-compose -f {file}'
    if rocket:
        if task in ('local', 'run', 'exec', 'down'):
            compose += ' -f docker/docker-compose.rocket.yml'
        elif task != 'rocket':
            exit('Rocket.Chat cannot be enabled during this task')

    if task == 'single':
        do(f'{docker} run'
           f'  -v `pwd`:/app'
           f'  -p {port}:8000'
           f'  -u {os.getuid()}'
           f'  -it ej/app:latest {cmd or "bash"}')
    elif task == 'local':
        do(f'{compose} run -p {port}:8000 {app} {cmd or "bash"}')
        do(f'{compose} stop')
    elif task in ('up', 'down'):
        do(f'{compose} {task}')
    elif task in ('run', 'exec'):
        do(f'{compose} -p {port}:8000 {task} {app} {cmd or "bash"}')
    else:
        raise SystemExit(f'invalid task: {task}')
    if clean_perms:
        do(f'sudo chown `whoami`:`whoami` * -R')


@task(
    help={
        **HELP_MESSAGES,
        'build-kit': 'Build-kit is an experimental Docker feature that usually leads to faster builds',
        'org': 'Organization owning the Docker images',
        'tag': 'Tag for the resulting Docker image',
        'which': 'Select image to build (base, local or deploy)',
    },
)
def docker_build(ctx, theme=None, dry_run=False, build_kit=False,
                 org='ej', tag='latest'):
    """
    Rebuild all docker images for the project.
    """
    from subprocess import check_output

    os.chdir(directory)
    theme, _ = set_theme(theme)
    prefix = 'DOCKER_BUILDKIT=1 ' if build_kit else ''
    do = runner(ctx, dry_run, pty=True)
    cmd = su_docker(f'{prefix}docker build . -f docker/Dockerfile ')
    env = {
        'ORG': org,
        'TAG': tag,
        'THEME': theme,
        'COMMIT_TITLE': check_output('git log -n 1 --format="%s"', shell=True).strip(),
        'COMMIT_HASH': check_output('git log -n 1 --format="%H"', shell=True).strip(),
    }
    cmd += ' '.join(f'--build-arg {k}={v}' for k, v in env.items())
    requirements(ctx)
    do(cmd + f' -t {org}/web:{tag} --target deploy')
    do(cmd + f' -t {org}/app:{tag} --target local')


@task(
    help={
        **HELP_MESSAGES,
        'spec': 'A string or list of strings of the form <theme>:<org>',
    },
)
def docker_push(ctx, tag='latest', spec='default:ejplatform', dry_run=False):
    """
    Build and push docker images for the web container.
    """
    cmd = su_docker(f'docker push')
    do = runner(ctx, dry_run, pty=True)

    for item in spec.split(','):
        spec, org = item.split(':') if ':' in item else (item, item)
        do(f'{cmd} {org}/web:{tag}')


#
# Translations
#
@task(
    help={
        'compile': 'Compile .po files',
        'edit': 'Open poedit to edit translations',
        'lang': 'Language',
        'keep-pot': 'If true, do not clean up temporary .pot files (debug)',
    },
)
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
        manage(ctx, 'makemessages', keep_pot=True, locale=lang)

        print('Extract Jinja translations')
        ctx.run('pybabel extract -F etc/babel.cfg -o locale/jinja2.pot .')

        print('Join Django + Jinja translation files')
        ctx.run('msgcat locale/django.pot locale/jinja2.pot --use-first -o locale/join.pot',
                pty=True)
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
def lint(ctx):
    """
    Execute linters
    """
    ctx.run('flake8 src/', pty=True)


@task
def clean(ctx):
    """
    Clean pyc files and build assets.
    """
    join = os.path.join
    rm_files = []
    rm_dirs = []
    for base, subdirs, files in os.walk('.'):
        if '__pycache__' in subdirs:
            rm_dirs.append(join(base, '__pycache__'))
        elif os.path.basename(base) == '__pycache__':
            rm_files.extend(join(base, f) for f in files)

    print('Removing compiled bytecode files')
    for path in rm_files:
        os.unlink(path)
    for path in rm_dirs:
        os.rmdir(path)


@task
def install_hooks(ctx):
    """
    Install git hooks in repository.
    """
    print('Installing flake8 pre-commit hook')
    ctx.run('flake8 --install-hook=git')


@task
def configure(ctx, silent=False, dev=True):
    """
    Install dependencies and configure a test server.
    """
    if silent:
        ask = (lambda x: print(x + 'yes') or True)
    else:
        ask = (lambda x: input(x + ' (y/n) ')[0].lower() == 'y')

    # Update requirements
    requirements(ctx)

    if ask('\nInstall dependencies?'):
        suffix = ' -r etc/requirements-dev.txt' if dev else ''
        ctx.run(f'{python} -m pip install markupsafe toolz')
        ctx.run(f'{python} -m pip install sidekick')
        ctx.run(f'{python} -m pip install -r etc/requirements.txt' + suffix)

    if ask('\nInstall js dependencies?'):
        cwd = os.getcwd()
        os.chdir(cwd + '/lib')
        try:
            ctx.run('npm install')
        finally:
            os.chdir(cwd)

    if ask('\nInitialize database (inv db)?'):
        db(ctx)
        if ask('\nLoad assets to database (inv db-assets)?'):
            db_assets(ctx)
        if ask('\nLoad fake data to database (inv db-fake)?'):
            db_fake(ctx)

    if ask('\nCompile js assets? (inv js)?'):
        js(ctx)
    if ask('\nCompile CSS resources (inv sass)?'):
        sass(ctx)
    if ask('\nCompile translations (inv i18n -c)?'):
        i18n(ctx, compile=True)
    if ask('\nBuild documentation (inv docs)?'):
        docs(ctx)


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


@task(
    help={
        'verbose': 'Detailed error messages',
        'lf': 'Run only the last failed tests',
    }
)
def test(ctx, verbose=False, lf=False):
    """
    Run all unittests.
    """
    opts = ''
    if verbose:
        opts += ' -vv'
    if lf:
        opts += ' --lf'
    ctx.run(f'pytest {opts}', env={
        'EJ_THEME': 'default',
        'EJ_BASE_URL': 'localhost',
        'USE_I18N': 'false',
        'USE_L10N': 'false',
        'USE_TZ': 'false',
        'COUNTRY': '',
    })


@task
def lint(ctx, python=True, js=True):
    """
    Run all linters.
    """
    if python:
        ctx.run('flake8 src/')
    if js:
        print('NOT IMPLEMENTED')


@task(name='manage')
def manage_task(ctx, command, noinput=False, args=''):
    """
    Run a Django manage.py command
    """
    kwargs = {}
    if noinput:
        kwargs['noinput'] = noinput
    manage(ctx, f'{command} {args}', **kwargs)


@task
def collect(ctx, theme=None):
    """
    Runs Django's collectstatic command
    """
    theme, root = set_theme(theme)
    root_css = directory / 'lib/build/css/'
    root_js = directory / 'lib/build/js/'

    # Select the correct minified build for CSS assets
    for file in ['main', 'rocket', 'hicontrast']:
        from_path = root_css / (file + f'-{theme}.min.css')
        to_path = root_css / (file + '.css')
        if not from_path.exists():
            print('Please run "inv build-assets" first!', file=sys.stderr)
        with open(to_path, 'w') as fd:
            fd.write(open(from_path).read())

    # Select minified javascript assets
    for file in os.listdir(root_js):
        if file.endswith('.min.js'):
            from_path = root_js / file
            to_path = root_js / (file[:-6] + 'js')
            if not from_path.exists():
                print('Please run "inv build-assets" first!', file=sys.stderr)
            with open(to_path, 'w') as fd:
                fd.write(open(from_path).read())

    manage(ctx, 'collectstatic --noinput')


#
# Deploy tasks
#
@task
def docker_deploy(ctx, task, environment='production', command=None, dry_run=False):
    """
    Start a deploy build for the platform.
    """
    os.environ.update(environment=environment, task=task)
    compose_file = 'local/deploy/docker-compose.deploy.yml'
    env = docker_deploy_variables('local/deploy/config.py')
    compose = su_docker(f'docker-compose -f {compose_file}')
    do = runner(ctx, dry_run, pty=True, env=env)
    tag = env.get('TAG', 'latest')
    org = env.get('ORGANIZATION', 'ejplatform')

    if task == 'build':
        do(f'{compose} build')
    elif task == 'up':
        do(f'{compose} up')
    elif task == 'run':
        do(f'{compose} run web {command or "bash"}')
    elif task == 'publish':
        docker = su_docker('docker')
        do(f'{docker} pull {org}/web:{tag}')
    elif task == 'notify':
        listeners = env.get('LISTENERS')
        if listeners is None:
            print("Don't know how to notify the infrastructure!")
            print('(hmm, mail the sysadmin?)')
        for listener in listeners.split(','):
            do(f'sh local/deploy/notify.{listener}.sh')
    else:
        raise SystemExit(f'invalid command: {task}\n'
                         f'Possible commands: build, up, run, publish, notify')


#
# Tools
#
@task
def notebook(ctx):
    """
    Start a notebook server.
    """

    base = Path(directory)
    db_path = os.path.abspath(base / 'local' / 'db' / 'db.sqlite3')
    ctx.run('jupyter-notebook', env={
        'PYTHONPATH': base / 'src',
        'DJANGO_SETTINGS_MODULE': 'ej.settings',
        'DJANGO_DB_URL': f'sqlite:///{db_path}'
    })


#
# Services
#
@task
def rocket(ctx, dry_run=False, command='up', background=False):
    """
    Run a Rocket.Chat instance using docker.
    """
    go = runner(ctx, dry_run, pty=True)
    compose = su_docker('docker-compose')
    suffix = '-d ' if background else ''
    go(f'{compose} -f docker/docker-compose.rocket.yml {suffix}{command}')


#
# Utilities
#
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
            return ctx.run(cmd, **kwargs)

    return do


def docker_deploy_variables(path):
    ns = {}
    seq = (list, tuple)
    to_str = (lambda x: ','.join(map(str, x)) if isinstance(x, seq) else str(x))
    with open(path) as fd:
        src = fd.read()
        exec(src, ns)
    return {k: to_str(v) for k, v in ns.items() if k.isupper()}


def set_theme(theme):
    if theme and '/' in theme:
        theme = theme.rstrip('/')
        root = f'{theme}/'
        theme = os.path.basename(theme)
    elif theme and theme != 'default':
        root = f'lib/themes/{theme}/'
    elif 'EJ_THEME' in os.environ:
        theme = os.environ['EJ_THEME']
        root = 'lib/' if theme == 'default' else f'lib/themes/{theme}/'
    else:
        theme = 'default'
        root = 'lib/'

    os.environ['EJ_THEME'] = theme
    return theme, root


def watch_path(path, func, poll_time=0.5, name=None, skip_first=False):
    """
    Watch path and execute the given function everytime a file changes.
    """
    import time
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent, \
        FileDeletedEvent, FileModifiedEvent, FileMovedEvent

    file_event = (FileCreatedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent)
    last = time.time()

    def dispatch(ev):
        nonlocal last

        if (ev.src_path.endswith('__') or ev.src_path.startswith('__')
            or ev.src_path.startswith('~') or ev.src_path.startswith('.')):
            return

        if isinstance(ev, file_event):
            last = start = time.time()
            time.sleep(poll_time)
            if last == start:
                print(f'File modified: {ev.src_path}')
                func()

    observer = Observer()
    handler = FileSystemEventHandler()
    handler.dispatch = dispatch
    observer.schedule(handler, path, recursive=True)
    observer.start()
    name = name or func.__name__
    print(f'Running {name} in watch mode.')
    if not skip_first:
        func()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def exec_watch(path, func, name, watch=False, background=False, poll_time=0.5):
    if watch and background:
        go = lambda: watch_path(path, func, name=name, poll_time=poll_time)
        return exec_watch(path, go, name, background=True)
    elif watch:
        return watch_path(path, func, name=name, poll_time=poll_time)
    elif background:
        from threading import Thread

        def go():
            try:
                func()
            except KeyboardInterrupt:
                pass

        thread = Thread(target=go, daemon=True)
        thread.start()
    else:
        func()
