==============================
Login utilizando redes sociais
==============================

Usuários podem entrar no EJ com a conta do Twitter ou Facebook, também. Para isso, é necessário preparar o ambiente e criar os apps sociais nas respectivas redes sociais.

Twitter
=======

Primeiro, vá para a interface de desenvolvedor do Twitter (https://apps.twitter.com) e crie um app. O ponto principal é definir as "Callback URLs" e marcar a caixa "Allow this application to be used to Sign in with Twitter". Por favor adicione duas URLs de callback: https://your-host/accounts/twitter/login/callback/ e http://your-host/accounts/twitter/login/callback/.

Agora, no Django, vá para a interface de administração e crie um novo aplicativo social: http://localhost:8000/admin/socialaccount/socialapp/add/. Escolha o provedor "Twitter", coloque um nome tipo "EJ Twitter", escolha o site ejplatform.org.br e coloque a consumer key no campo "Client id" e consumer secret no campo "Secret key". Você pode encontrar a consumer key e consumer secret na página do aplicativo do Twitter, na aba "Keys and Access Tokens".

Facebook
========

Importante ter em mente: Facebook apenas permite HTTPS e não permite localhost. Então, para desenvolvimento local, sugerimos ferramentas como Local Tunnel (http://localtunnel.github.io/www/) ou Ngrok (https://ngrok.com/) para ter uma URL HTTPS pública que redireciona para sua instância local do EJ. Lembre-se de adicionar este host ao DJANGO_ALLOWED_HOSTS.

Uma vez com o host em mãos, vá para a interface de gerenciamento de aplicativos do Facebook (https://developers.facebook.com/apps) e adicione um novo aplicativo web. Vá para Configurações > Básico e adicione o host a "Domínios do aplicativo" e "Site". Adicione o produto "Login do Facebook" à sua aplicação e, nas suas configurações, adicione https://your-host/accounts/facebook/login/callback como um URIs de redirecionamento do OAuth válido.

Agora, no Django, vá para a interface de administração e crie um novo aplicativo social: http://localhost:8000/admin/socialaccount/socialapp/add/. Escolha o provedor "Facebook", coloque um nome tipo "EJ Facebook", escolha o site ejplatform.org.br e coloque o id do aplicativo no campo "Client id" e a chave secreta do aplicativo no campo "Secret key". Você pode encontrar ambos na página do aplicativo do Facebook, em Configurações > Básico.

Google
======

Para permitir login via conta do Google, é necessário um domínio de primeiro nível válido em que você possa confirmar a propriedade. Vá para a interface de administração de aplicativos (https://console.developers.google.com/) e crie um projeto. Crie uma nova credencial e adicione https://your-host/accounts/google/login/callback/ como URI de redirecionamento autorizada. Lembre-se também de adicionar o domínio como um domínio válido.

Agora, no Django, vá para a interface de administração e crie um novo aplicativo social: http://localhost:8000/admin/socialaccount/socialapp/add/. Escolha o provedor "Google", coloque um nome tipo "EJ Google", escolha o site ejplatform.org.br e coloque o id do aplicativo no campo "Client id" e a chave secreta do aplicativo no campo "Secret key". Você pode encontrar ambos na página do aplicativo do Google, em Credenciais.

Outras informações
==================

Para todos os casos, para desenvolvimento local, você pode também precisar definir, em src/ej/settings/__init__.py, ACCOUNT_EMAIL_VERIFICATION = 'none'.

Mais detalhes em https://django-allauth.readthedocs.io/en/latest/providers.html.
