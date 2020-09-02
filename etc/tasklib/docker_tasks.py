import os

from invoke import task

from .base import HELP_MESSAGES, su_docker, runner, directory, set_theme, docker_deploy_variables
from .build_tasks import requirements

__all__ = ["docker", "docker_build", "docker_deploy", "docker_push", "rocket"]


@task(
    help={
        **HELP_MESSAGES,
        "task": 'One of "local", "single", "up", "down", "run", "exec" or "rocket"',
        "rocket": "Enable Rocket.Chat",
    }
)
def docker(ctx, task, dry_run=False, build=False):
    """
        Runs EJ platform using a docker container.
        """
    if task == "up":
        docker = su_docker("docker")
        do = runner(ctx, dry_run, pty=True)
        # file = prepare_dockerfile(cmd, file, deploy)
        file = "docker/docker-compose.yml"
        # compose = prepare_compose_cmd(file, task, rocket, docker)
        if(build):
            compose = f"docker-compose -f {file}"
            do(f'{compose} up  -d  --build')
        else:
            compose = f"docker-compose -f {file}"
            do(f'{compose} up  -d')
    if task == "stop":
        docker = su_docker("docker")
        do = runner(ctx, dry_run, pty=True)
        # file = prepare_dockerfile(cmd, file, deploy)
        file = "docker/docker-compose.yml"
        # compose = prepare_compose_cmd(file, task, rocket, docker)
        compose = f"docker-compose -f {file}"
        do(f'{compose} stop')


@task(
    help={
        **HELP_MESSAGES,
        "build-kit": "Build-kit is an experimental Docker feature that usually leads to faster builds",
        "org": "Organization owning the Docker images",
        "tag": "Tag for the resulting Docker image",
        "which": "Select image to build (base, local or deploy)",
    }
)
def docker_build(ctx, theme=None, dry_run=False, build_kit=False, org="ej", tag="latest"):
    """
    Rebuild all docker images for the project.
    """
    from subprocess import check_output

    os.chdir(str(directory))
    theme, _ = set_theme(theme)
    prefix = "DOCKER_BUILDKIT=1 " if build_kit else ""
    do = runner(ctx, dry_run, pty=True)
    cmd = su_docker(f"{prefix}docker build . -f docker/Dockerfile ")
    env = {
        "ORG": org,
        "TAG": tag,
        "THEME": theme,
        "COMMIT_TITLE": check_output('git log -n 1 --format="%s"', shell=True).strip(),
        "COMMIT_HASH": check_output('git log -n 1 --format="%H"', shell=True).strip(),
    }
    cmd += " ".join(f"--build-arg {k}={v}" for k, v in env.items())
    requirements(ctx)
    do(cmd + f" -t {org}/web:{tag} --target deploy")
    do(cmd + f" -t {org}/app:{tag} --target local")


@task
def docker_deploy(ctx, task, environment="production", command=None, dry_run=False):
    """
    Start a deploy build for the platform.
    """

    os.environ.update(environment=environment, task=task)
    compose_file = "local/deploy/docker-compose.deploy.yml"
    env = docker_deploy_variables("local/deploy/config.py")
    compose = su_docker(f"docker-compose -f {compose_file}")
    do = runner(ctx, dry_run, pty=True, env=env)
    tag = env.get("TAG", "latest")
    org = env.get("ORGANIZATION", "ejplatform")

    if task == "build":
        do(f"{compose} build")
    elif task == "up":
        do(f"{compose} up")
    elif task == "run":
        do(f'{compose} run web {command or "bash"}')
    elif task == "publish":
        docker = su_docker("docker")
        do(f"{docker} pull {org}/web:{tag}")
    elif task == "notify":
        listeners = env.get("LISTENERS")
        if listeners is None:
            print("Don't know how to notify the infrastructure!")
            print("(hmm, mail the sysadmin?)")
        for listener in listeners.split(","):
            do(f"sh local/deploy/notify.{listener}.sh")
    else:
        raise SystemExit(f"invalid command: {task}\n" f"Possible commands: build, up, run, publish, notify")


@task(help={**HELP_MESSAGES, "spec": "A string or list of strings of the form <theme>:<org>"})
def docker_push(ctx, tag="latest", spec="default:ejplatform", dry_run=False):
    """
    Build and push docker images for the web container.
    """
    cmd = su_docker(f"docker push")
    do = runner(ctx, dry_run, pty=True)

    for item in spec.split(","):
        spec, org = item.split(":") if ":" in item else (item, item)
        do(f"{cmd} {org}/web:{tag}")


@task
def rocket(ctx, dry_run=False, command="up", background=False):
    """
    Run a Rocket.Chat instance using docker.
    """
    go = runner(ctx, dry_run, pty=True)
    compose = su_docker("docker-compose")
    suffix = "-d " if background else ""
    go(f"{compose} -f docker/docker-compose.rocket.yml {suffix}{command}")


def prepare_dockerfile(cmd, file, deploy):
    if cmd == "rocket":
        return "docker/docker-compose.rocket.yml"
    elif file is None and deploy:
        return "docker/docker-compose.deploy.yml"
    elif file is None:
        return "docker/docker-compose.local.yml"
    return file


def prepare_compose_cmd(file, task, rocket, docker):
    compose = f"{docker}-compose -f {file}"
    if rocket:
        if task in ("local", "run", "exec", "down"):
            compose += " -f docker/docker-compose.rocket.yml"
        elif task != "rocket":
            exit("Rocket.Chat cannot be enabled during this task")
    return compose
