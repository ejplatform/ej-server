# Empurrando Juntos

Projeto Django baseado no padrão [cookiecutter-django](http://cookiecutter-django.readthedocs.io/en/latest).

## Ambiente de desenvolvimento

Para clonar este repositório e seus [submódulos](https://git-scm.com/book/en/v2/Git-Tools-Submodules), execute:

`git clone --recursive git@gitlab.com:empurrandojuntos/backend.git`

Levante o ambiente de desenvolvimento com `docker-compose -f local.yml up` e acesse [localhost:8000](http://localhost:8000).

Se você já tiver a pasta de um submódulo no seu ambiente local, mas ela estiver vazia, execute o seguinte comando dentro dela:

`git submodule update --init --recursive`

### Atualização de submódulos ('git pull' de repositórios internos)

Dependendo do seu papel neste projeto como desenvovedor, há duas maneiras de lidar com submódulos:

- Você não modifica repositórios internos: execute o `git pull` tradicional seguido de `git submodule update --recursive`. Com esses comandos, você sempre terá a última versão fixada deles no repositório-pai

- Você modifica repositórios internos: entre na pasta do submódulo e use `git checkout` para seguir um branch. Para publicar suas modificações na app principal, além de usar `commit` e `push` no repositório-filho, é necessário repetir esse processo no repositório-pai

## Testes

Existem duas maneiras de se executar os testes automatizados localmente:

- Você já executou o comando `docker-compose -f local.yml up` e o servidor está funcionando.

```
docker-compose -f local.yml exec django pytest
```

- Você deseja apenas executar os testes sem necessariamente levantar toda a infraestrutura fornecida no ambiente local, o arquivo de configuração do docker-compose `test.yml` irá construir apenas o django e o postgres.

```
docker-compose -f test.yml up
```


## Variáveis de ambiente
### Banco de dados
- POSTGRES_HOST - opcional; padrão 'postgres'
- POSTGRES_DB - obrigatório
- POSTGRES_USER - obrigatório
- POSTGRES_PASSWORD - obrigatório

### Email
- MAILGUN_SENDER_DOMAIN - obrigatório em produção
- DJANGO_DEFAULT_FROM_EMAIL - obrigatório em produção
- DJANGO_MAILGUN_API_KEY - obrigatório em produção

### Django
- DJANGO_ALLOWED_HOSTS - obrigatório em produção
- DJANGO_ADMIN_URL - opcional
- DJANGO_SETTINGS_MODULE - opcional; use `config.settings.production` em produção
- DJANGO_ACCOUNT_ALLOW_REGISTRATION - opcional; padrão True
- DJANGO_SECRET_KEY - obrigatório em produção
- USE_CACHE - opcional; padrão True
- USE_DOCKER - opcional; desnecessário em produção; em ambientes locais, escreva 'yes' se estiver usando Docker

### ReCaptha
- DJANGO_RECAPTCHA_PRIVATE_KEY - obrigatório em produção
- DJANGO_RECAPTCHA_PUBLIC_KEY - obrigatório em produção

### Redis
- REDIS_URL - obrigatório em produção; exemplo: `redis://127.0.0.1:6379`

### Sentry
- DJANGO_SENTRY_DSN - opcional; só válido em produção

### django-courier
- COURIER_ONESIGNAL_USER_ID - obrigatório
- COURIER_ONESIGNAL_APP_ID - obrigatório
- COURIER_DEFAULT_PROVIDER - obrigatório

## Depoly em produção

Um exemplo de deploy em produção pode ser encontrado no arquivo `production.yml`.

Para rodá-lo localmente, e assim ter o máximo de aderência com o ambiente final, cire um arquivo `.env` baseado em `env.example` com as configurações necessárias e execute:

```
docker-compose -f production.yml up
```

## Integrações de deploy
**Commits no branch `master`** fazem releases da versão em **desenvolvimento** (ainda sem URL pública).

**Tags** fazem releases em [**produção**](https://ej.brasilqueopovoquer.org.br/).
