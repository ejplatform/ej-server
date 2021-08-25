===========
EJ Platform
===========

You can visit EJ website at https://ejplatform.org.
For detailed information on developing and using our system, you can access our documentation on:
https://www.ejplatform.org/docs/.
For contributions, issues or feature requests join us on https://gitlab.com/pencillabs/ej/ej-application

Getting started
===============

Local development (Docker)
------------------------------

First clone the repository::

    $ git clone https://gitlab.com/pencillabs/ej/ej-server
    $ cd ej-server

The recomended way to run EJ is with Docker. With it 
you can quickly start the development server using the
commands::

    $ sudo pip3 install invoke==1.4.1 --user
    $ inv docker-up
    $ inv docker-logs

This will deploy EJ using **docker/docker-compose.yml** file.
Every change made on the repository will be reflected inside the
`docker_server` container.

If you are creating a clean EJ instance, you can populate de database
with some fake data::

    $ inv docker-exec "inv db-fake"

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

==================  ============================================= 
Command             Description  
==================  =============================================
inv i18n            Compile translations
inv sass            Compile sass files
inv sass --watch    Watch changes on code, and compile .sass files
inv db              Prepare database and run migrations
==================  =============================================

Documentation
-------------

Documentation can be updated with::

    $ inv docker-exec "inv docs"
    
will be available at the ``build/docs/`` directory.

Changing theme
--------------

The previous commands build EJ using the "default" theme. EJ accepts additional
themes and currently comes pre-installed with the alternate "cpa" theme. The
first step is to rebuild static assets::

    $ inv docker-exec "inv js db-assets"
    $ inv docker-exec "inv sass -t cpa" 

Now run the server using the --theme flag::

    $ inv docker-exec "inv run -t cpa"

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
