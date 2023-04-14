===========
EJ Platform
===========


You can visit EJ website at https://www.ejplatform.org.
For detailed information on developing and using our system, you can access our documentation on:
https://www.ejplatform.org/docs/.
For contributions, issues or feature requests join us on https://gitlab.com/pencillabs/ej/ej-application

Getting started
===============

Local development (Docker)
------------------------------

First clone the repository::

    $ git clone https://gitlab.com/pencillabs/ej/ej-application
    $ cd ej-application

The recomended way to run EJ is with Docker. With it
you can quickly start the development server using the
commands::

    $ pip3 install invoke==2.0.0 --user
    $ inv docker-build
    $ inv docker-up

This will deploy EJ using **docker/docker-compose.yml** file.
Every change made on the repository will be reflected inside the
`docker_server` container.

If you are creating a clean EJ instance, you can populate de database
with some fake data::

    $ inv docker-exec "poetry run inv db-fake"

You can access the running instance accessing `http://localhost:8000`.

To rebuild the server image, you can run `inv docker-build --no-cache`.

Some useful commands to manage docker environment:

==================  =============================================
Command             Description
==================  =============================================
inv docker-up       Creates EJ containers and run the application
inv docker-logs     Shows django logs
inv docker-stop     Stops EJ containers
inv docker-rm       Removes EJ containers
inv docker-attach   Connects to django container
inv docker-exec     Executes a command on django container
==================  =============================================

Some useful commands to manage the application (run this inside django container):

===========================  ======================================================
Command                      Description
===========================  ======================================================
poetry run inv i18n          Extracts messages from Jinja templates for translation
poetry run inv i18n -c       Compile .po files
poetry run inv sass          Compile sass files
poetry run inv sass --watch  Watch changes on code, and compile .sass files
poetry run inv db            Prepare database and run migrations
===========================  ======================================================


Tests
-----

If you are making changes to EJ codebase, do not forget to run tests frequently.
EJ uses Pytest_::

    $ inv docker-test

Docker bash
-----------

You probably will want to execute commands inside the container.
It is possible to open a bash shell in the main "web" container with::

    $ inv docker-attach

You also can execute commands without open docker bash shell::

    $ inv docker-exec "command"

Documentation
-------------

After configuring local environment, the next step is reading our documentation. It can be generated with::

    $ inv docker-exec "poetry run inv docs"

and will be available at the `http://localhost:8000/docs <http://localhost:8000/docs>`_ url.
