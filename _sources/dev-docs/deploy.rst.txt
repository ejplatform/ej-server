==========
Deployment
==========

EJ relies on Docker and a Docker orchestration technology such as Docker Compose
in its deployment process.

The easiest way to proceed is to use the pre-build images available on `Docker Hub`_
and personalize your installation using environment variables. You must
understand that a basic EJ stack uses 3 containers described in `EJ Architecture`_
session: the Nginx reverse proxy, the Django application and a Postgres
database.

.. _Docker Hub: https://hub.docker.com/u/ejplatform/
.. _EJ Architecture: architecture.html

The first step is to build the deployment image for the main application. You
must have a working development environment in your machine. Activate the virtualenv
using ``workon ej`` and then enter the command::

    $ inv docker-build --deploy

The docker-build command accepts additional configurations such as
``--theme cpa``, ``--country brasil``, ``--tag v1.0``, and others
(``inv docker-build -h`` shows additional options).

After building the image, you must initialize the database. Open a terminal in
the Django container with the command::

    $ inv docker run --deploy

Now execute the commands to populate the database::

    $ python manage.py migrate ej_users
    $ inv db db-assets

(you can also add db-fake to add fake data and test users).

Finally, fire all containers using::

    $ inv docker up --deploy

The EJ instance should be available at port 80.

**Observation**

The ``inv docker *`` tasks are simply alias to longer docker-compose commands.
If you want to discover the equivalent docker command, add the --dry-run option
to any command.

::

    $ inv docker up --deploy

You will see that it is equivalent to::

    sudo docker-compose -f docker/docker-compose.deploy.yml up


Configuration
=============

EJ is configured using `Environment Variables`_. Those variables can be
conveniently set up in the files inside the /docker/env/ folder. Edit those
files and then run ``$ inv docker up --deploy`` in order to update the container
with the new configurations. Bear in mind that many of the configuration
variables are secrets that cannot be shared in a public location. Because of this,
we recommend to store the environment files on a private fork of the main
repository.

.. _Environment Variables: environment-variables.html


Rocket.Chat integration
=======================

Integrating Rocket.Chat to the stack requires a few additional steps. You must
edit the docker/env/django.env file and set ``EJ_ROCKETCHAT_INTEGRATION=true``.
Depending on your configuration, you might need to set other environment variables
such as EJ_ROCKETCHAT_URL and EJ_ROCKETCHAT_USERNAME.

You can start the Rocket.Chat containers either running

::

    $ sudo docker-compose -f docker/docker-compose.rocket.yml up

or by adding a flag --rocket after the ``docker up`` command

::

    $ inv docker up --deploy --rocket

In order to integrate the main EJ application with an instance of Rocket.Chat,
open your Rocket.Chat url and you will be redirected to /setup-wizard, create
an admin user and configure the server. After you finish the setup-wizard, the
next step is to login as an the superuser in EJ and point to <EJ URL>/talks/config/.
This URL presents a form to configure the basic parameters of Rocket.Chat integration.
Here you have to provide the admin credentials you created on Rocket.Chat setup-wizard.

Now, go to the Rocket.Chat administration page. It will be something like
``http://<rocket-host>/admin/Accounts``. Setup the
`IFrame login integration`_ at ``Administration > Accounts > IFrame``.

.. _Rocket.Chat API docs: https://rocket.chat/docs/developer-guides/rest-api/
.. _IFrame login integration: https://rocket.chat/docs/developer-guides/iframe-integration/authentication/

In this page, follow the instructions bellow:

1. Set the ``Enabled`` option to ``True``.
2. In order to enable redirection after successful *login*, set ``Iframe URL``
   to ``http://<django-host>/talks/login/?next=/talks/`` (replacing Django with the
   address of your actual Django instance).
3. Rocket.Chat needs to check if an user is already authenticated. Set
   ``API URL`` to ``http://<django-host>/talks/check-login/``.
4. Set ``API Method`` to ``POST``.
5. Save the changes.

Now, go to ``Administration > Accounts`` and disable the following features:

* Allow changes to user profile
* Allow

The final step is to setup EJ using a superuser account. Go to http://<django-host>/talks/
and it will request additional information before continuing.

Now each time you try to access Rocket.Chat without Django authentication, the
user will be redirected to the EJ login page.


Rocket.Chat style
-----------------

It is possible to override the default style and some static content in the
website. Go to ``Administration > Layout > Content`` and save the content of the
home page there. We recommend to keep this data versioned in the configuration
repository. Similarly, it is possible to set a custom CSS and save it using
Rocket.Chat admin page at at ``Administration > Layout > Custom CSS``.

The following command makes a few automatic customizations to the Rocket.Chat
account::

    $ sudo docker-compose -f docker/docker-compose.rocket.yml exec mongo bash

This command opens a bash CLI and must be executed while Mongo db is running on
the background. Now execute ``mongo /scripts/mongo_script.js`` on the terminal.
