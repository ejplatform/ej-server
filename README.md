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

## Rocketchat Integration

To deploy the rocketchat local server, you can run its custom docker-compose file:

```bash
sudo docker-compose -f rocketchat.yml
```

To integrate _ej-server_ with this instance of Rocketchat, first you need to get the rocketchat admin user **token**, and **id**. So, first visit `localhost:3000` and create your admin user. For this example, let's treat his name as _rcadmin_. To get his information call the Rocketchat API using curl:

```bash
curl http://localhost:3000/api/v1/login \
     -d "username=rcadmin&password=rcadminpassword"
```

There are other ways to retrieve this data via API. Visit [Rocketchat API docs;](https://rocket.chat/docs/developer-guides/rest-api/authentication/login/).

Now, go to the Rocketchat administration page and setup the [IFrame login integration](https://rocket.chat/docs/developer-guides/iframe-integration/authentication/). Find `Administration > Accounts > IFrame` page. Using _localhost_ it will be `http://localhost:3000/admin/Accounts`.

1. Set `Enabled` option to `True`
2. Enable redirection after success _login_, set `Iframe URL` to `http://localhost:8000/login/?next=/api/v1/rocketchat/redirect`.
3. Rocketchat needs to check if an user is already authenticated. Set `API URL` to `http://localhost:8000/api/v1/rocketchat/check-login`.
4. `API Method` must be `POST`
5. Save changes

You have to modify some Django settings to complete the integration. First go to `Django Admin > Constance (Config) > RocketChat Options`.

* `ROCKETCHAT_URL`: set to the external accessible Rocketchat URL, `http://localhost:3000`.
* `ROCKETCHAT_PRIVATE_URL`: set to the rocketchat docker internal network address `http://rocketchat:3000`, or leave blank if there is no rocketchat private URL.
* `ROCKETCHAT_AUTH_TOKEN`: set to the admin token got on the `curl` command.
* `ROCKETCHAT_USER_ID`: set to the admin ID got on the `curl` command.

Now each time you try to access Rocketchat without django authentication, the user will be redirected to the EJ login page.
