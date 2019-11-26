from fabric import task


@task
def install(ctx, repo="ej-server", deploy="{repo}/deploy", from_="deploy"):
    """
    Install basic system packages and optionally prepare a development
    environment in the host.
    """
    deploy = deploy.format(repo=repo)
    raise NotImplementedError


@task
def rebuild(ctx, repo="ej-server", deploy="{repo}/deploy"):
    """
    Update git repository and rebuild images.
    """
    deploy = deploy.format(repo=repo)
    ctx.run(f"cd {repo} && git pull")
    ctx.run(f"cd {deploy} && docker-compose build")


@task
def update(ctx, repo="ej-server", deploy="{repo}/deploy", migrate=True, build=True):
    """
    Update repository, rebuild images and restart application.
    """
    deploy = deploy.format(repo=repo)

    if build:
        rebuild(ctx, repo=repo, deploy=deploy)

    ctx.run(f"cd {deploy} && docker-compose stop web")
    if migrate:
        ctx.run(f"cd {deploy} && docker-compose run web db -m")
    ctx.run(f"cd {deploy} && docker-compose up -d")


@task
def docker_compose(ctx, cmd, repo="ej-server", deploy="{repo}/deploy", interactive=True):
    """
    Execute docker-compose with command.
    """
    deploy = deploy.format(repo=repo)
    ctx.run(f"cd {deploy} && docker-compose {cmd}", pty=interactive)


@task
def inv(ctx, cmd, repo="ej-server", deploy="{repo}/deploy", interactive=True):
    """
    Execute invoke task in the "web" container.
    """
    deploy = deploy.format(repo=repo)
    ctx.run(f"cd {deploy} && docker-compose run web {cmd}", pty=interactive)


@task
def bash(ctx, repo="ej-server", deploy="{repo}/deploy", docker=False, root=False):
    """
    Execute a bash instance on remote directory. If --docker, opens the bash
    shell of the main "web" container.
    """
    deploy = deploy.format(repo=repo)
    if docker:
        opts = ""
        if root:
            opts += " -u root"
        ctx.run(f"cd {deploy} && docker-compose run {opts} web bash", pty=True)
    else:
        ctx.run(f"cd {repo} && bash", pty=True)
