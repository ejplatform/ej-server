======
Deploy
======

EJ relies on Docker and a Docker orchestration technology such as Docker Compose
in its deployment process.

The easiest way to proceed is to use the pre-build images available on `Docker Hub`_
and personalize your installation using environment variables. You must
understand that a basic EJ stack uses 3 containers described in `EJ Architecture`_
session: the Nginx reverse proxy, the Django application and Postgres
databases.

.. _Docker Hub: https://hub.docker.com/u/ejplatform/
.. _EJ Architecture: architecture.html

The first step is to build the deployment image for the main application. You
must have a working development environment in your machine and just type in
the prompt::

    $ inv docker-build --deploy

The docker-build command accepts additional configurations such as ``--theme cpa``,
``--tag v1.0`` and others (``inv docker-build -h`` shows additional options).


Docker compose
==============

A standard build of EJ can be easily run using docker-compose. In very simple
scenarios in which no customization is necessary, this is all you need to deploy
EJ. All you need is to call the command bellow from the ej-server repository::

    $ inv docker-run production

This is actually a shortcut for the longer list of Docker Compose commands
that builds and run the stack::

    $ sudo docker-compose -f docker/docker-compose.production.yml build
    $ sudo docker-compose -f docker/docker-compose.production.yml up

This is all fine for testing, but it is very likely to fail in a real life
situation. You need to provide specific configurations such as the domain name,
credentials to different services, the location and passwords of your database
server, etc.

In order to make things simple, we created an example repository with a bare
bones Docker Compose configuration that you can adapt to your own use case.
Start by cloning it to the local/deploy folder with the command::

    $ git clone https://github.com/ejplatform/docker-compose-deploy.git local/deploy/

This will copy the example files to local/deploy. This folder is ignored by git
versioning and you can maintain it as a private repository independent of
``ejplatform/ej-server``.

Adapt the files on this folder to your needs by setting the values of all
necessary `Environment Variables`_. In the long run, it is probably best to use
a private repository to keep those files with version control. Bear in mind that
many of the configuration variables are secrets that cannot be shared in a
public location.

.. _Environment Variables: environment-variables.html

Now rebuild the deployment images using the command::

    $ inv docker-deploy build

and

::

    $ inv docker-deploy up

to execute the stack.


Configuration
=============

The standard structure of the docker-compose-deploy_ repository implement a few
options that the ``inv docker-deploy`` task understand. We list a few useful
commands bellow:

.. _docker-compose-deploy: https://github.com/ejplatform/docker-compose-deploy/

``inv docker-deploy build``:
    Builds all images necessary for the Docker Compose file to run.

``inv docker-deploy up``:
    Executes the full stack using Docker Compose.

``inv docker-deploy run -c bash``:
    Executes the full stack and runs the given command in the Django container.
    It can be any task registered in tasks.py. The command bellow uses the
    "bash" task to open a bash shell in the container.

``inv docker-deploy publish``:
    Publish all images in Docker Hub.

``inv docker-deploy notify``:
    Notify your stack that all images were updated. We implement a script that
    integrates with Rancher, but you can override this script and use any
    integration you like.

All those commands accept a ``-e ENVIRONMENT`` option that allows us to specify
different environments other than "production". A common pattern is to use two
separate deploys: the "production" and "staging" environments. All environments
share the same docker images, but uses different Docker Compose files.


config.py
---------

This script is executed and it must define a JSON-like structure that is used
to fill the environment variables passed to docker-compose when starting the
containers. The main variables defined on config.py are listed bellow:

ORGANIZATION (ejplatform):
    Name of organization or user in Docker Hub used to store images. It defaults
    to  ejplatform, but you need to change to some organization that you can
    publish images to.

TAG (latest):
    Release number for the built images. Leave as "latest" if desired.

THEME (default):
    Theme used to construct images. This sets the EJ_THEME variable in the
    docker container.

LISTENERS:
    A list of listeners that implement the notify command. Each listener must
    have a corresponding notify.<listener>.sh script. We provide an example
    using Rancher.

The `config.py` file can also be used to set arbitrary configuration variables
that are injected in the environment.


Rocket.Chat integration
=======================

Integrating Rocket.Chat to the stack requires a few additional steps. The first
step is to uncomment all services in the Rocket.Chat section of the example
docker-compose.yml file to enable the necessary containers.

You also need to set the following environment variable either in config.env or
in the docker-compose.yml file:

``EJ_ROCKETCHAT_INTEGRATION=true``:
    If true, enables the Rocket chat integration in the Django application.
    Remember to configure the docker-compose.yml file accordingly.

Now build the containers and execute compose:

    $ inv docker-deploy build
    $ inv docker-deploy up

In order to integrate the main EJ application with an instance of Rocket.Chat,
open your Rocket.Chat url and you will be redirected to /setup-wizard, create
an admin user and configure the server. After you finish the setup-wizard, the
next step is to login as an the superuser in EJ and point to <EJ URL>/talks/config/.
This URL presents a form that you can be used to configure the basic parameters of
Rocket.Chat integration, here you have to put the admin credentials you created
on Rocket.Chat setup-wizard.

There are other ways to retrieve this data from the API. Visit
`Rocket.Chat API docs`_ to learn more.



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

Follow the tutorial_ for further explanations (in Portuguese).

.. _tutorial: https://drive.google.com/file/d/1LoEMIU4XwaypUJe1D2na8R1Qf4Fwxgy4/view
