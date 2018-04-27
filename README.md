| Environment | CI Status |  Website |
|:-:|:-:|:-:|
| Production | [![pipeline status](https://gitlab.com/ejplatform/ej-server/badges/master/pipeline.svg)](https://gitlab.com/ejplatform/ej-server/commits/master) | [ejplatform.org](https://ejplatform.org) |
| Development | [![pipeline status](https://gitlab.com/ejplatform/ej-server/badges/develop/pipeline.svg)](https://gitlab.com/ejplatform/ej-server/commits/develop) | [dev.ejplatform.org](http://dev.ejplatform.org) |

# ejplatform

Django project template inspired on [cookiecutter-django](http://cookiecutter-django.readthedocs.io/en/latest) directives.

## Development Environment

To clone this repository and its [submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules), execute:

```shell
git clone --recursive git@github.com:ejplatform/ej-server.git
```

If you already have a empty folder of a submodule in you local project, execute this command:

```shell
git submodule update --init --recursive
```

To make your local environment up and running using docker-compose, execute:

```shell
sudo docker-compose -f ./docker/local/build.yml build
sudo docker-compose -f ./docker/local/start.yml up -d
```

After the command, **ej-server** can be accessed at [http://localhost:8000](http://localhost:8000).

### Submodule Update (`git pull` in internal repositories)

Depending of your role on this project as a developer, there are two manners to deal with submodules:

* If you do not modify internal repositories:
    * Execute: `git pull`;
    * Execute: `git submodule update --recursive`;
    * With this instructions you will get the latest version fixed on upstream repository.
* If you modify internal repositories:
    * Access the folder containing the submodule;
    * Execute: `git checkout` to select a desired branch;
    * To publish your modifications in the main app, besides using `commit` and `push` on this repository, it is necessary to repeat this process in the upstream repository.

## Tests

There are two ways of executing locally the automated tests using docker-compose:

* If you already ran `sudo docker-compose -f ./docker/local/start.yml up -d` and the server is up and running, execute:

```bash
sudo docker-compose -f ./docker/local/start.yml exec django pytest
```

* If you just want to run the tests without necessarily getting up all the services available on local environment, the configuration file on docker-compose [docker/local/test.yml](https://github.com/ejplatform/ej-server/blob/master/docker/local/test.yml) will have only the necessary services to run the tests. To run the tests, execute:

```bash
sudo docker-compose -f ./docker/local/test.yml run --rm django
```

## Environment Variables

The [env.example](https://github.com/ejplatform/ej-server/blob/master/env.example) file has all the environment variables defined to **ej-server**.

Additionally, the docker-compose environment variables files are defined on their own directory:

* [docker/local/start.yml](https://github.com/ejplatform/ej-server/blob/master/docker/local/start.yml): [docker/local/env/*.env](https://github.com/ejplatform/ej-server/tree/master/docker/local/env)
* [docker/local/idle.yml](https://github.com/ejplatform/ej-server/blob/master/docker/local/idle.yml): [docker/local/env/*.env](https://github.com/ejplatform/ej-server/tree/master/docker/local/env)
* [docker/local/test.yml](https://github.com/ejplatform/ej-server/blob/master/docker/local/test.yml): [docker/local/env/*.test.env](https://github.com/ejplatform/ej-server/tree/master/docker/local/env)
* [docker/production/deploy.example.yml](https://github.com/ejplatform/ej-server/blob/master/docker/production/deploy.example.yml): Example defined on itself

## Deployment

An example of deploy in production using docker-compose can be found in [docker/production/deploy.example.yml](https://github.com/ejplatform/ej-server/blob/master/docker/production/deploy.example.yml).

## Continuous Integration

Every commit at any branch will run the `test` stage from the `pipeline`.

Commits at `base` branch will upgrade the `ej-server:base`, `ej-server:base-test`, and `ej-server:base-production` images. Commits at `base` branch can only be performed if it contain changes in [requirements/base.txt](https://github.com/ejplatform/ej-server/blob/master/requirements/base.txt).

Commits at `base_test` branch will upgrade the `ej-server:base-test` image. Commits at `base_test` branch can only be performed if it contain changes in [requirements/test.txt](https://github.com/ejplatform/ej-server/blob/master/requirements/test.txt).

Commits at `base_production` branch will upgrade the `ej-server:base-production` image. Commits at `base_production` branch can only be performed if it contain changes in [requirements/production.txt](https://github.com/ejplatform/ej-server/blob/master/requirements/production.txt).

## Continuous Deployment

Commits at `develop` branch will release to [http://dev.ejplatform.org](http://dev.ejplatform.org).

Commits at `master` branch will release to [https://ejplatform.org](https://ejplatform.org).

## Rocketchat Integration

See the guidelines at [docker/extensions](https://github.com/ejplatform/ej-server/blob/master/docker/extensions#using-rocketchat).
