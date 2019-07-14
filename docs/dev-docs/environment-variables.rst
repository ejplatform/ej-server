=====================
Environment Variables
=====================


EJ uses 12-factor approach to configuration and uses environment variables to
customize most behavior and settings of the platform. The environment variables
can either be set directly on the host environment, or saved to a environment
file so they can be shared between different environments. This section describes
the main configuration variables with their standard values.


Basic settings
==============

Those are the minimum set of required configurations. **Warning:** Remember
reading the "Security" section before completing your deploy.

DJANGO_HOSTNAME (localhost):
    Host name for the EJ application. Can be something like "ejplatform.org".
    This is the address in which your instance is deployed.

COUNTRY (Brazil):
    Country used for localization and internationalization. This configuration
    controls simultaneously the DJANGO_LOCALE_NAME, DJANGO_LANGUAGE_CODE,
    DJANGO_TIME_ZONE variables using the default configurations for your
    country. Countries are specified by name (e.g., USA, Brazil, Argentina,
    Canada, etc). You can use a COUNTRY as base and personalize any variable
    of those variables independently (e.g., COUNTRY="Canada",
    LANGUAGE_CODE="fr-ca")

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


Security
========

**DJANGO_SECRET_KEY** (random value):
    A random string of text that should be out of public sight. This string is
    used to negotiate sessions and for encryption in some parts of Django. This
    can be a random sequence of characters that is treated as a secret since in
    theory an attacker that knows the secret key could use this value to forge
    sessions and impersonate other users.



Personalization
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


Rules and limits
----------------

EJ_ENABLE_BOARDS (true):
    The default behavior is that each user can own a single board of
    conversations independent of the main board under /conversations/.
    Set to "false" in order to disable those personal boards.

EJ_MAX_COMMENTS_PER_CONVERSATION (2):
    Default number of comments that each user has in each conversation.

EJ_EXCLUDE_PROFILE_FIELDS:
    Optional list of fields that should be excluded from user profile
    visualization.


Integration with Rocket.Chat
============================

EJ_ROCKETCHAT_INTEGRATION (false):
    Enable/disable integration with Rocket.Chat. It is necessary to configure
    the Rocket.Chat container if this option is enabled.

EJ_ROCKETCHAT_URL:
    Public URL of Rocket.Chat instance (e.g.: http://localhost:3000 or https://your-chat-instance.com)

EJ_ROCKETCHAT_API_URL:
    Internal URL used to access Rocket.Chat on the intranet. Used to make
    API requests.

EJ_ROCKETCHAT_USERNAME:
    Username of Rocket.Chat admin.

EJ_ROCKETCHAT_AUTH_TOKEN:
    Authentication token for the Rocket.Chat admin. This can be configured
    in Django backend after initial installation. Check `Rocket API`_ for more
    information.

EJ_ROCKETCHAT_USER_ID:
    Unique id of Rocket.Chat admin.

EJ_ROCKETCHAT_PASSWORD:
    Rocket.Chat admin password.

.. _Rocket API: https://rocket.chat/docs/developer-guides/rest-api/authentication/
