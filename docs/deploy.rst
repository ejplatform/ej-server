Deploy
========

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

    $ sudo docker-compose -f docker/docker-compose.example.yml build
    $ sudo docker-compose -f docker/docker-compose.example.yml up

This is all fine for testing, but it is very likely to fail in a real
installation. You probably need to provide many specific configurations such
as the domain name, credentials to lots of different services, the location of
your database server, etc.





Environment Variables
---------------------

The
`env.example <https://github.com/ejplatform/ej-server/blob/master/env.example>`__
file has all the environment variables defined to **ej-server**.

Additionally, the docker-compose environment variables files are defined
on their own directory:

-  `docker/local/start.yml <https://github.com/ejplatform/ej-server/blob/master/docker/local/start.yml>`__:
   `docker/local/env/*.env <https://github.com/ejplatform/ej-server/tree/master/docker/local/env>`__
-  `docker/local/idle.yml <https://github.com/ejplatform/ej-server/blob/master/docker/local/idle.yml>`__:
   `docker/local/env/*.env <https://github.com/ejplatform/ej-server/tree/master/docker/local/env>`__
-  `docker/local/test.yml <https://github.com/ejplatform/ej-server/blob/master/docker/local/test.yml>`__:
   `docker/local/env/*.test.env <https://github.com/ejplatform/ej-server/tree/master/docker/local/env>`__
-  `docker/production/deploy.example.yml <https://github.com/ejplatform/ej-server/blob/master/docker/production/deploy.example.yml>`__:
   Example defined on itself

Deployment
----------

An example of deploy in production using docker-compose can be found in
`docker/production/deploy.example.yml <https://github.com/ejplatform/ej-server/blob/master/docker/production/deploy.example.yml>`__.

Continuous Deployment
---------------------

Commits at ``develop`` branch will release to http://dev.ejplatform.org.

Commits at ``master`` branch will release to https://ejplatform.org.

