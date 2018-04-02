| Environment | ej-server CI Status | ej-front CI Status |  Website |
|:-:|:-:|:-:|:-:|
| Development | [![pipeline status](https://gitlab.com/ejplatform/ej-server/badges/develop/pipeline.svg)](https://gitlab.com/ejplatform/ej-server/commits/develop) | [![pipeline status](https://gitlab.com/ejplatform/ej-front/badges/develop/pipeline.svg)](https://gitlab.com/ejplatform/ej-front/commits/develop) | [dev.ejplatform.org](http://dev.ejplatform.org) |
| Production | [![pipeline status](https://gitlab.com/ejplatform/ej-server/badges/master/pipeline.svg)](https://gitlab.com/ejplatform/ej-server/commits/master) | [![pipeline status](https://gitlab.com/ejplatform/ej-front/badges/master/pipeline.svg)](https://gitlab.com/ejplatform/ej-front/commits/master) | [ejplatform.org](https://ejplatform.org) |

# ejplatform

Django project template based on [cookiecutter-django](http://cookiecutter-django.readthedocs.io/en/latest) directives.

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
sudo docker-compose -f local.yml up
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

* If you already ran `docker-compose -f local.yml up` and the server is up and running, execute:

```bash
sudo docker-compose -f local.yml exec django pytest
```

* If you just want to run the tests without necessarily getting up all the services available on local environment, the configuration file on docker-compose [test.yml](https://github.com/ejplatform/ej-server/blob/master/test.yml) will have only the necessary services to run the tests. To run the tests, execute:

```bash
sudo docker-compose -f test.yml run --rm django
```

## Environment Variables

The [env.example](https://github.com/ejplatform/ej-server/blob/master/env.example) file has all the environment variables defined to **ej-server**.

Additionally, the docker-compose environment variables files are defined on their own directory:

* [local.yml](https://github.com/ejplatform/ej-server/blob/master/local.yml): [compose/local/*.env](https://github.com/ejplatform/ej-server/tree/master/compose/local)
* [test.yml](https://github.com/ejplatform/ej-server/blob/master/test.yml): [compose/dev/*.env](https://github.com/ejplatform/ej-server/tree/master/compose/dev)
* [production.yml](https://github.com/ejplatform/ej-server/blob/master/production.yml): Example defined on itself

## Deploy in production

An example of deploy in production using docker-compose can be found in [production.yml](https://github.com/ejplatform/ej-server/blob/master/production.yml).

## Deploy integrations

Commits at `develop` branch will release to [http://dev.ejplatform.org](http://dev.ejplatform.org)

Commits at `master` branch will release to [https://ejplatform.org](https://ejplatform.org)
