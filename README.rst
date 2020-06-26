.. image:: https://api.codeclimate.com/v1/badges/fd8f8c7d5d2bc74c38df/maintainability
   :target: https://codeclimate.com/github/ejplatform/ej-server/maintainability
   :alt: Maintainability
.. image:: https://codecov.io/gh/ejplatform/ej-server/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/ejplatform/ej-server
.. image:: https://gitlab.com/ejplatform/ej-server/badges/master/pipeline.svg
    :target: https://gitlab.com/ejplatform/ej-server/commits/master


===========
EJ Platform
===========

You can visit EJ website at http://ejplatform.org.

Getting started
===============

First clone the repository::

    $ git clone http://github.com/ejplatform/ej-server/
    $ cd ej-server

If you use Docker, you can quickly start the development server using the
commands::

    $ sudo pip3 install invoke --user
    $ inv docker-build
    $ inv docker up

Finally, populate db with the fake users::

    $ inv docker exec -c "inv db-fake"

For most cases, however, we recommend that you prepare your machine with some
extra tools. Developers may choose between Docker or Poetry/Virtualenv for day to day
development. In both cases, we recommend that you have Invoke_ installed
in your machine to make execution of chores easier.


Local development (virtualenv)
------------------------------

This is a list of packages that you should have installed locally before we
start:

- Python 3.7
- Virtualenv or virtualenvwrapper
- Invoke (>= 1.0)
- Node.js and npm
- Gettext
- Docker (optional, for deployment)

You can install all dependencies on recent Ubuntu/Debian variants with the
following commands::

    $ sudo apt install python3-dev python3-pip virtualenvwrapper \
                       npm gettext docker.io docker-compose
    $ sudo pip3 install invoke

Once everything is installed, create and activate your virtualenv. We will create
a new virtualenv called "ej"::

    $ mkvirtualenv --python=python3.7 ej

This command creates and activates the virtualenv with python3.7. When you want to work with the
repository in a later time, activate the virtual env using the command ``workon ej``.

The following steps are handled by the configure.sh script::

    $ sh configure.sh

This task creates a test database with a few conversations, users, comments, and
votes. Notably, it automatically creates an admin user ``password: admin, email: admin@admin.com``
a regular user ``password: user, email: user@user.com``.

This step takes some time. Grab a cup of coffee while it downloads and install
all dependencies. If everything works as expected, you should be able to run
the server using the ``inv run`` command after it is finished.


Running it
----------

Unless you prefer to type long Django management commands, use Invoke_ to start
the dev server::

    $ inv run

You can control many configurations using environment variables. To run using
the Brazilian Portuguese translation, for instance, just export the correct
COUNTRY setting::

    $ export COUNTRY=brasil

Depending on your network configurations, you might need to set the ``ALLOWED_HOSTS``
setting for your Django installation. This is a basic security setting that
controls which hosts can serve pages securely. In non-production settings, set
``DJANGO_ALLOWED_HOSTS`` environment variable to * to allow connections in any
network topology::

    $ DJANGO_ALLOWED_HOSTS=*

Invoke manages many other important tasks, you can discover them using::

    $ inv -l

.. _Invoke: http://www.pyinvoke.org/

Documentation
-------------

Documentation can be updated with::

    $ inv docs 
    
will be available at the ``build/docs/`` directory.

------

with docker:

    $ inv docker exec -c "inv docs"

Changing theme
--------------

The previous commands build EJ using the "default" theme. EJ accepts additional
themes and currently comes pre-installed with the alternate "cpa" theme. The
first step is to rebuild static assets::

    $ inv js db-assets
    $ inv sass -t cpa 

Now run the server using the --theme flag::

    $ inv run -t cpa

Tests
-----

If you are making changes to EJ codebase, do not forget to run tests frequently.
EJ uses Pytest_::

    $ inv test

------

with docker:

    $ inv docker exec -c "inv test"

.. _Pytest: https://docs.pytest.org/

Docker bash
-----------

You probably will want to execute commands inside the container.
It is possible to open a bash shell in the main "web" container with::

    $ inv docker run

You also can execute commands without open docker bash shell::

    $ inv docker exec -c " command "