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


## Produção

Um exemplo de deploy em produção pode ser encontrado no arquivo `production.yml`.

Para rodá-lo localmente, e assim tem o máximo de aderência com o ambiente final, cire um arquivo `.env` baseado em `env.example` com as configurações necessárias e execute:

```
docker-compose -f production.yml up
```

## Deploy

**Commits no branch `master`** fazem releases da versão em **desenvolvimento** (ainda sem URL pública).

**Tags** fazem releases em [**produção**](https://ej.brasilqueopovoquer.org.br/).
