Deploy
======

EJ relies on Docker and a Docker orchestration technology for its deployment
process. We assume, by simplicity, that your deployment is going to use Docker
Compose. It will work with other technologies (we use Rancher, for instance),
but of course we cannot anticipate the details of your infrastructure and
Docker Compose is a useful reference for many other orchestration technologies.

The easiest way to proceed is to use the pre-build images available on `Docker Hub`_
and personalize your installation using environment variables. You must
understand that a basic EJ stack uses 4 containers described in `EJ Stack`_
session: the Nginx reverse proxy, the Django application and Redis and Postgres
databases.

.. _Docker Hub:: https://hub.docker.com/u/ejplatform/

You can run a useful "deployable" stack by simply calling the command from the
ej-server repository::

    $ inv docker-run deploy

This is actually a shortcut for the longer list of Docker Compose commands
that builds and run the stack::

    $ sudo docker-compose -f docker/docker-compose.deploy.yml build
    $ sudo docker-compose -f docker/docker-compose.deploy.yml up

This is all fine for testing, but it is very likely to fail in a real life
situation. You probably need to provide many specific configurations such
as the domain name, credentials to different services, the location and passwords
to your database server, etc.

In order to make things simple, we created an example repository with a bare
bones Docker Compose configuration that you can adapt to your own project.
Start by cloning it with the command::

    $ git clone https://github.com/ejplatform/docker-compose-deploy.git local/deploy/

This will copy the example files to local/deploy. This folder is ignored by git
versioning and you can maintain it as a private repository independent of
``ejplatform/ej-server``. Now, adapt the files on this folder to your needs by
setting the values of the `Environment Variables`_ you need to modify. In the
long run, it is probably best to use a private repository to save those files
with version control. Bear in mind that many of the configuration variables are
secrets that cannot be seen in a public location.

Now rebuild the deployment images using the command::

    $ inv docker-deploy build

and

    $ inv docker-deploy up

to execute the stack.

Deployment configuration
------------------------

The standard structure of docker-compose-deploy has a few options that the
``inv docker-deploy`` sub-tasks understand.

config.json
~~~~~~~~~~~

The config.json tweaks how the images are built.

"organization" (ejplatform):
    Name of organization or user in Docker Hub used to store images. It defaults
    to  ejplatform, but you should probably change to some organization that you
    control.
"tag" (latest):
    Release number for the built images. Can leave at "latest" if desired.
"theme" (default):
    Theme used to construct images.


Environment Variables
~~~~~~~~~~~~~~~~~~~~~

The list of environment variables with their default values.

Basic
.....

DJANGO_HOSTNAME (localhost):
    Host name for the EJ application. Can be something like "ejplatform.org".
    This is the address in which your instance is deployed.

Security
........

DJANGO_SECRET_KEY (random value):
    A random string of text that should be out of public sight. This string is
    used to negotiate sessions and for encryption in some parts of Django.


Options
.......

EJ_ROCKETCHAT_INTEGRATION (false):
    If true, enables the Rocket chat integration in the Django application.
    You still need to configure the docker-compose.yml file accordingly.

Personalization
...............

EJ_PAGE_TITLE (Empurrando Juntos):
    Default title of the home page.

Rules and limits
................

EJ_CONVERSATIONS_ALLOW_PERSONAL_CONVERSATIONS (true):
    The default behavior is that each user can own a single timeline of
    conversations independent of the main timeline under /conversations/.
    Set to "false" in order to disable those personal timelines.
EJ_CONVERSATIONS_MAX_COMMENTS (2):
    Default number of comments that each user has in each conversation.


Continuous Deployment
---------------------

The default EJ instance at http://ejplatform.org uses a system of continuous
integration/continuous deploy that you might want to replicate in your
organization.

# TODO.
