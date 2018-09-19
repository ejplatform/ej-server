Deploy
======

EJ relies on Docker and a Docker orchestration technology for its deployment
process. We assume, for simplicity, that your deployment is going to use Docker
Compose. It works with other technologies (we use Rancher, for instance),
but of course we cannot anticipate the details of your infrastructure to provide
a detailed guide. Docker Compose is a useful reference and common ground for many
other orchestration technologies.

The easiest way to proceed is to use the pre-build images available on `Docker Hub`_
and personalize your installation using environment variables. You must
understand that a basic EJ stack uses 4 containers described in `EJ Stack`_
session: the Nginx reverse proxy, the Django application and Redis and Postgres
databases.

.. _Docker Hub:: https://hub.docker.com/u/ejplatform/

You can run a useful "deployable" stack by simply calling the command bellow from
the ej-server repository::

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
``ejplatform/ej-server``. Now, adapt the files on this folder to your needs by
setting the values of all necessary `Environment Variables`_. In the
long run, it is probably best to use a private repository to save those files
with version control. Bear in mind that many of the configuration variables are
secrets that cannot be seen in a public location.

Now rebuild the deployment images using the command::

    $ inv docker-deploy build

and

    $ inv docker-deploy up

to execute the stack.


Configuration
-------------

The standard structure of the docker-compose-deploy_ repository implement a few
options that the ``inv docker-deploy`` sub-tasks understand. We list those tasks
bellow:

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
separate deploys: the "production" "staging" environments. All environments
share the same docker images, but uses different Docker Compose files.


config.py
~~~~~~~~~

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


Environment Variables
~~~~~~~~~~~~~~~~~~~~~

All the environment variables bellow can be set directly within the docker-compose
files or at config.env so they can be shared between different environments.
This section describes the main configuration variables with their standard
values.

Basic and security
..................

Those are the minimum set of required configurations.

**DJANGO_SECRET_KEY** (random value):
    A random string of text that should be out of public sight. This string is
    used to negotiate sessions and for encryption in some parts of Django. This
    can be any random that is treated as a secret since in theory an attacker
    that knows the secret key could use this value to forge sessions and
    impersonate other users.

HOSTNAME (localhost):
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


Personalization
...............

EJ_PAGE_TITLE (Empurrando Juntos):
    Default title of the home page.

Rules and limits
................

EJ_CONVERSATIONS_ALLOW_PERSONAL_CONVERSATIONS (true):
    The default behavior is that each user can own a single board of
    conversations independent of the main board under /conversations/.
    Set to "false" in order to disable those personal boards.
EJ_CONVERSATIONS_MAX_COMMENTS (2):
    Default number of comments that each user has in each conversation.


Rocketchat integration
----------------------

Integrating Rocketchat to the stack requires a few additional steps. The first
step is to uncomment all services in the Rocketchat section of the example
docker-compose.yml file to enable the necessary containers.

You also need to set the following environment variable either in config.env or
in the docker-compose.yml file:

EJ_ROCKETCHAT_INTEGRATION=true:
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
`Rocketchat API docs`_ to learn more.

Now, go to the Rocket.Chat administration page. It will be something like
``http://your-rocket.chat-hostname/admin/Accounts``. Setup the
`IFrame login integration`_ at ``Administration > Accounts > IFrame``.

.. _Rocketchat API docs: https://rocket.chat/docs/developer-guides/rest-api/
.. _IFrame login integration: https://rocket.chat/docs/developer-guides/iframe-integration/authentication/

In this page, follow the instructions bellow:

1. Set ``Enabled`` option to ``True``.
2. In order to enable redirection after successful *login*, set ``Iframe URL``
   to ``http://django:8000/login/?next=/talks/`` (replacing Django with the
   address of your actual Django instance).
3. Rocketchat needs to check if an user is already authenticated. Set
   ``API URL`` to ``http://django-hostname/talks/check-login/``.
4. Set ``API Method`` to ``POST``.
5. Save the changes.

Now, go to ``Administration > Accounts`` and disable the following features:

* Allow changes to user profile
* Allow

The final step is to setup EJ using a superuser account. Go to http://<hostname>/talks/
and it will request additional information before continuing.

Now each time you try to access Rocketchat without django
authentication, the user will be redirected to the EJ login page.


Rocketchat style
----------------

It is possible to override the default style and some static content in the
website. Go to ``Administration > Layout > Content`` and save the content of the
home page there. We recommend to keep this data versioned in the configuration
repository. Similarly, it is possible to set a custom CSS and save it using
Rocketchat admin page at at ``Administration > Layout > Custom CSS``.

Follow the tutorial_ for further explanations (in Portuguese).

.. _tutorial: https://drive.google.com/file/d/1LoEMIU4XwaypUJe1D2na8R1Qf4Fwxgy4/view
