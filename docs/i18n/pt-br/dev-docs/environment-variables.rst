=====================
Variáveis de Ambiente
=====================

.. contents::
   :depth: 2

EJ usa variáveis de ambiente para personalizar a maioria dos comportamentos e configurações da plataforma.
As variáveis de ambiente podem ser definidas diretamente no ambiente host ou salvo em um arquivo de
ambiente (.env) para que possam ser compartilhados entre diferentes ambientes. Esta seção descreve
as principais variáveis de configuração com seus valores padrão.


Basic settings
==============

Esse é o conjunto mínimo de variáveis necessárias, entre parentêses encontra-se o seu valor padrão. **Aviso:** Lembre-se
de ler a seção "Segurança", mais abaixo, antes de concluir sua implantação.

DJANGO_HOSTNAME (localhost):
    Nome do host para o aplicativo EJ. Pode ser algo como "ejplatform.org".
    Este é o endereço no qual sua instância é implantada.

COUNTRY (Brazil):
    O País é utilizado para localização e internacionalização da plataforma. Esta configuração
    controla simultaneamente as variáveis DJANGO_LOCALE_NAME, DJANGO_LANGUAGE_CODE
    e DJANGO_TIME_ZONE usando as configurações padrão para o seu
    país. Os países são especificados pelo nome (por exemplo, USA, Brazil, Argentina,
    Canadá, etc). Você pode usar um PAÍS como base e personalizar qualquer variável
    de forma independente (por exemplo, COUNTRY = "Canadá", LANGUAGE_CODE = "fr-ca")

DJANGO_DEBUG (False):
    Setting DEBUG=True, display a traceback when Django encounters an error. This
    configuration is useful in a staging environment, but should never be enabled
    in the final production build.

DJANGO_DB_URL (psql://<user>:<password>@postgres:5432/<dbname>):
    Describes the connection with the Postgres database. The default unsafe values
    are ``user = password = dbname = "ej"``. You can change to other database types
    or configurations (e.g., sqlite:///path-to-db-file). **Warning:** The way
    Django parses this string puts some limitations on valid passwords. Stay
    safe and use only letters and numbers in the password.


Segurança
=========

**DJANGO_SECRET_KEY** (random value):
    A random string of text that should be out of public sight. This string is
    used to negotiate sessions and for encryption in some parts of Django. This
    can be a random sequence of characters that is treated as a secret since in
    theory an attacker that knows the secret key could use this value to forge
    sessions and impersonate other users.


Personalização
===============

Those variables customize the behavior of the EJ platform in different ways.

Override strings
-----------------

EJ_PAGE_TITLE (Empurrando Juntos):
    Default title of the home page.

EJ_REGISTER_TEXT (Not part of EJ yet?):
    Text displayed requesting user registration.

EJ_LOGIN_TITLE_TEXT (Login in EJ):
    Asks user login.


Override paths
--------------

EJ_ANONYMOUS_HOME_PATH (/start/):
    Redirect users to this path before login.

EJ_USER_HOME_PATH (/conversations/):
    Redirect logged users to this path.


Regras e Limites
----------------

EJ_ENABLE_BOARDS (true):
    The default behavior is that each user can own a single board of
    conversations independent of the main board under /conversations/.
    Set to "false" in order to disable those personal boards.

EJ_MAX_COMMENTS_PER_CONVERSATION (2):
    Default number of comments that each user has in each conversation.

EJ_PROFILE_EXCLUDE_FIELDS:
    Optional list of fields that should be excluded from user profile
    visualization.

