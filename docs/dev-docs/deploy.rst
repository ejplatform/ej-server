==========
Deployment
==========

EJ recommends using Docker with a container orchestration technology such as
Docker Compose in its deployment process.

The easiest way to proceed is to use the pre-build images available on `Docker Hub`_
and personalize your installation using environment variables. You must
understand that a basic EJ stack uses 3 containers described in `EJ Architecture`_
session: the Nginx reverse proxy, the Django application and a Postgres
database.

.. _Docker Hub: https://hub.docker.com/u/ejplatform/
.. _EJ Architecture: architecture.html


Building images
===============

EJ provides a few pre-build images on Docker-hub. This is enough for most users,
but if you are developing new features, or making some advanced customization,
or for just a matter of policy, it will be necessary to build your own images
manually.

EJ requires a relatively recent version of Docker (17.05+) that supports
multi-stage builds. We recommend that you customize the provided docker-compose
files for the specific needs of your own organization proceeding.

Copy some files under the docker folder to a separate folder (ideally under
private source control). We assume this folder is called ``deploy``,
which is conveniently registered on .gitignore in the main ej-server repository::

    $ cp -r docker/ deploy/

For your own convenience, rename docker-compose.deploy.yml so we don't need to
use the ``-f`` flag on all compose commands::

    $ cd deploy/
    $ mv docker-compose.deploy.yml docker-compose.yml

You may want change some configurations in this file and customize the
important ``config.env`` file in this folder. Both files are self-explanatory
and have lots of comments, so read them with patience and set the correct values.
**ATTENTION:** you **must** edit config.env file and change at least the secret key,
otherwise the security of your installation will be compromised.

You can also check the section on the `Environment Variables`_ used by EJ.
Bear in mind that many of the configuration variables are secrets that cannot
be shared in a public location. Because of this, we recommend to store the
environment file on a private repository.

.. _Environment Variables: environment-variables.html


Now use docker-compose to build and start the containers::

    $ docker-compose.yml build
    $ docker-compose.yml up

Grab a coffee and when you come back your system should be up and running :)


Docker-build
------------

If you are in a hurry or do not need to customize the build process too much,
consider using the docker-build shortcut::

    $ inv docker-build

This command accepts additional configurations (see: ``inv docker-build -h``).
Here are some important options you probably should set manually:


``--org, --tag``:
    Name image as '<org>/web:<tag>'
``--theme``:
    Defines the current theme. (E.g. ``--theme cpa``. EJ currently accepts
    "default" and "cpa").


Initializing the application
============================

After building the image, you will be greeted with a bare bones EJ instance.
We need to populate it with a few extra bits such as admin accounts, and perhaps
to load some fake data or old dumps from the database. Open a shell in the
"web" container so we can proceed with those extra steps::

    $ docker-compose run web bash

Once inside the container, you'll probably need to execute migrations and
create a superuser:

    $ python manage.py migrate
    $ python manage.py createsuperuser

Django's manage.py also has many other options that might be useful at this
stage. Run ``$ python manage.py`` to see what is available.

If you want to populate the database with some quick and dirty data, just type
the command bellow. ATTENTION: this pollutes the database with a lot of random
information and obviously should not be used in production!

    $ inv db-fake -h

Other potentially useful tasks are implemented on the invoke task file. Type
``inv -l`` to list them all. Notice the production image is very limited and
many tasks will not work because they require some missing dependencies.


Troubleshooting
---------------

**Static assets are not showing up correctly or are displaying the wrong theme**

Check if the EJ_THEME variable inside the "web" container is set correctly. If it
is so, maybe you need to collect static files again. Try the commands::

    $ inv collect
    $ python manage.py collectstatic

If even that fails, you might need to delete all contents from the volume and
initialize it again::

    $ rm /app/local/static/* -r
    $ inv collect

This can happen as the result of failed Docker builds or change in configuration
for images that use the same volume to hold static assets.


Rocket.Chat integration
=======================

Integrating Rocket.Chat to the stack requires a few additional steps. Remember to
set at least ``EJ_ROCKETCHAT_INTEGRATION=true`` on the ``config.env`` file.
This configuration enables the ``ej_rocketchat`` application, but does not
prepare the environment to connect to the Rocket.Chat instance.

The first step is to have a working Rocket.Chat instance. If you have not configured
it already, just complete the setup wizard that is displayed the first time
you access your Rocket.Chat instance. More crucially, remember the username
and password for the administrative account.

Depending on your configuration, you might prefer to set other environment
variables such as EJ_ROCKETCHAT_URL and EJ_ROCKETCHAT_USERNAME to create a fully
functional connection. However, the easier way to proceed is to configure the
integration using the wizard at http://<django-host>/talks/. Visit this URL
as a superuser and complete the form.

Regular users do not have permission to connect to Rocket.Chat. This permission
should be granted explicitly in the Django admin panel at http://<django-host>/admin/ej_users/user/
or http://<django-host>/admin/auth/group/. EJ creates an username and password
for each user allowed to connect to Rocket.Chat during the first attempt to login.

We still need a final configuration to make the integration functional.


Configuring Rocket.Chat
-----------------------

Go to the Rocket.Chat administration page as an administrative user at
http://<rocket-host>/admin/Accounts. We need to enable the `IFrame login integration`_
with Rocket.Chat. This system redirects an anonymous user that tries to access
Rocket.Chat to an IFrame that contains a login page for EJ. The user login in
and Rocket.Chat communicate with Django with an specific API endpoint.

We must set a few parameters for this to work. Go to ``Administration > Accounts > IFrame``.
In this page, follow the instructions:

1. Set the ``Enabled`` option to ``True``.
2. In order to enable redirection after successful *login*, set ``Iframe URL``
   to ``https://<django-host>/talks/login/?next=/talks/`` (replacing Django with the
   address of your actual Django instance).
3. Rocket.Chat needs to check if an user is already authenticated. Set
   ``API URL`` to ``https://<django-host>/talks/api-login/``.
4. Set ``API Method`` to ``POST``.
5. Save the changes.

This enables a bare bones integration, but leaves some dangerous options behind.
We must prevent users from modifying some aspects of their accounts from
Rocket.Chat, since they are now managed by EJ. Go to ``Administration > Accounts``
and disable *at least* the following features:

* Allow change username
* Allow change e-mail
* Allow change password


.. _Rocket.Chat API docs: https://rocket.chat/docs/developer-guides/rest-api/
.. _IFrame login integration: https://rocket.chat/docs/developer-guides/iframe-integration/authentication/


Troubleshooting
---------------

If you are receiving error messages for invalid IFrame requests, try to
set EJ_ROCKETCHAT_URL environment variable on config.env. If that still does not work,
change DJANGO_X_FRAME_OPTIONS and select the correct X-Frame-Options_ policy.

You might also want to include the rocket chat URL to the
DJANGO_CONTENT_SECURITY_POLICY_FRAME_ANCESTORS list in your environment file.
This is used to setup the frame-accessors part of the Content-Security-Policy_ header,
which is a more up-to-date way of setting up IFrame permissions.

.. _X-Frame-Options: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options
.. _Content-Security-Policy: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy


Rocket.Chat style and options
-----------------------------

It is possible to override the default style and some static content in the
website. Go to ``Administration > Layout > Content`` and save the content of the
home page there. We recommend to keep this data versioned in the configuration
repository. Similarly, it is possible to set a custom CSS and save it using
Rocket.Chat admin page at at ``Administration > Layout > Custom CSS``.

The following command makes a few automatic customizations to the Rocket.Chat
account::

    $ docker-compose exec mongo bash

This command opens a bash CLI and must be executed while Mongo db is running on
the background. Now execute ``mongo /scripts/mongo_script.js`` on the terminal.
