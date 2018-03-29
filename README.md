# EJ

Django structure based on [cookiecutter-django](http://cookiecutter-django.readthedocs.io/en/latest).

## Development Environment

To clone this repository and its [submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules), execute:

```shell
git clone --recursive git@gitlab.com:empurrandojuntos/backend.git
```

If you already have a empty folder of a submodule in you local project, execute this command:

```shell
git submodule update --init --recursive
```

To make your local environment up and running, execute:

```shell
sudo docker-compose -f local.yml up
```

After the command, **ej-server** can be accessed at [http://localhost:8000](http://localhost:8000).

### Submodule Update ('git pull' in internal repositories)

Depending of your role on this project as a developer, there are two manners to deal with submodules:

* If you do not modify internal repositories:
    * Execute: `git pull`;
    * Execute: `git submodule update --recursive`;
    * With this instructions you will always get the latest version fixed on parent repository.
* If you modify internal repositories:
    * Access the folder containing the submodule;
    * Execute: `git checkout` to select a desired branch;
    * To publish your modifications in the main app, besides using `commit` and `push` in your child repository, it is necessary to repeat this process in the parent repository.

## Tests

There are two ways of executing locally the automated tests:

* If you already ran `docker-compose -f local.yml up` and the server is up and running, execute:

```bash
docker-compose -f local.yml exec django pytest
```

* If you just want to run the tests without necessarily getting up all the services available on local environment, the configuration file on docker-compose `test.yml` will have only the necessary services to run the tests. To run the tests, execute:

```bash
docker-compose -f test.yml run --rm django
```

## Environment Variables

### Database

- POSTGRES_HOST - optional; default 'postgres'
- POSTGRES_DB - required
- POSTGRES_USER - required
- POSTGRES_PASSWORD - required

### Email

- MAILGUN_SENDER_DOMAIN - required in production
- DJANGO_DEFAULT_FROM_EMAIL - required in production
- DJANGO_MAILGUN_API_KEY - required in production

### Django

- DJANGO_ALLOWED_HOSTS - required in production
- DJANGO_ADMIN_URL - optional
- DJANGO_SETTINGS_MODULE - optional; use `config.settings.production` in production
- DJANGO_ACCOUNT_ALLOW_REGISTRATION - optional; default True
- DJANGO_SECRET_KEY - required in production
- USE_CACHE - optional; default True
- USE_DOCKER - optional; unnecessary in production; in local environments, write 'yes' if using Docker

### ReCaptcha

- DJANGO_RECAPTCHA_PRIVATE_KEY - required in production
- DJANGO_RECAPTCHA_PUBLIC_KEY - required in production

### Redis

- REDIS_URL - required in production; example: `redis://127.0.0.1:6379`

### Sentry

- DJANGO_SENTRY_DSN - optional; valid only in production

### django-courier

- COURIER_ONESIGNAL_USER_ID - required
- COURIER_ONESIGNAL_APP_ID - required
- COURIER_DEFAULT_PROVIDER - required

## Deploy in production

An example of deploy in production can be found in `production.yml`.

## Deploy integrations

Commits at `develop` branch will release to [http://dev.ejplatform.org](http://dev.ejplatform.org);

Commits at `master` branch will release to [http://dev.ejplatform.org](http://dev.ejplatform.org).
