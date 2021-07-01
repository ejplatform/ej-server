# Integração com Analytics

A EJ possui uma conta de serviço para se conectar na API do analytics. Essa conta permite, de forma autenticada, requisitar dados como tempo de sessão, paginas acessadas, e atividades do usuário na pagina monitorada. O email que identifica a conta de serviço, deve ser adicionado como usuário na propridade do Analytics, que armazena os dados de monitoramento. Sem isso, a EJ não terá permissão de requisitar os relatórios na API.

O arquivo `analytics_api.py` é reponsável por instanciar um cliente oauth2 para a API do analytics. As credenciais são lidas do arquivo `clients_secrets.json`.

Caso seja necessário gerar uma nova conta de serviço, os links abaixo documentam o processo:

- https://cloud.google.com/docs/authentication/production#auth-cloud-implicit-python
- https://cloud.google.com/iam/docs/best-practices-for-using-and-managing-service-accounts


O arquivo `clients_secrets.json`  do ambiente de produção não ficam armazenados no repositório.
