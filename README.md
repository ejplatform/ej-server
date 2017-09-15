# Empurrando Juntos

Projeto Django baseado no padrão [cookiecutter-django](http://cookiecutter-django.readthedocs.io/en/latest).

## Desenvolvimento

Para levantar uma versão local da plataforma com Docker use:

```
docker-compose -f local.yml up
```

## Produção
Um exemplo de deploy em produção pode ser encontrado no arquivo `production.yml`. 

Para rodá-lo localmente, e assim tem o máximo de aderência com o ambiente final, cire um arquivo `.env` baseado em `env.example` com as configurações necessárias e execute:

```
docker-compose -f production.yml up
```

## Deploy
**Commits no branch `master`** fazem releases da versão em **desenvolvimento** (ainda sem URL pública).

**Tags** fazem releases em [**produção**](https://ej.brasilqueopovoquer.org.br/).