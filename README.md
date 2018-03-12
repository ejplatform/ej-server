# EJ

Django project based on [cookiecutter-django](http://cookiecutter-django.readthedocs.io/en/latest).

## Development environment

To clone this repository and its [submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules), execute:

`git clone --recursive git@gitlab.com:empurrandojuntos/backend.git`

Get up and running your environment with `docker-compose -f local.yml up` and acess [localhost:8000](http://localhost:8000).

If you already have a empty folder of a submodule in you local, execute this command: 
`git submodule update --init --recursive`

### Submodule update ('git pull' in internal repositories)

Depending on your role in this project as a developer, there are two manners to deal with submodules:

- You do not modify internal repositories: execute a `git pull`, followed by `git submodule update --recursive`. With this instructions you will always get the latest version fixed on parent repository.
- You modify internal repositories: enter the folder containing the submodule and use `git checkout` to select a desired branch. To publish your modifications in the main app, besides using `commit` and `push` in your child repository, it is necessary to repeat this process in the parent repository.

## Tests

There are two ways of executing locally the automated tests:

- You already ran `docker-compose -f local.yml up` and the server is up.

```
docker-compose -f local.yml exec django pytest
```
- You just want to run the tests, without necessarily getting up all the infraestructure available on local environment, the configuration file on docker-compose `teste.yml` will get up only django and postgres. 

```
docker-compose -f test.yml up
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

An example of deploy in production can be found in `production.yml`

To run locally and simulate the production environment, create a file `.env` based on `env.example` with all necessary configurations, then run:
```
docker-compose -f production.yml up
```

## Deploy integrations
**Commits on branch `master`** create version releases on **development** (without public URL).

**Tags** Create releases on [**production**](https://ej.brasilqueopovoquer.org.br/).
