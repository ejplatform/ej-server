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

First clone the repository and point to it::

    $ git clone http://github.com/ejplatform/ej-server/
    $ cd ej-server

If you use docker, you can quickly start the development server using the
command::

    $ sudo docker-compose -f docker/docker-compose.yml up

For most cases, however, we recommend that you prepare your machine with some
tools. Developers may choose between docker or virtualenv for day to day
development. In both cases, we recommend that you have Invoke_ >= 1.0 installed
in your machine.

Docker will probably get you started quicker, but in the long run, it may be
harder to integrate with your tools and often requires long builds not needed when
using virtualenv.

_Invoke: http://www.pyinvoke.org/


Local development (virtualenv)
------------------------------

EJ platform **requires** you to _`Prepare environment` + with the
development headers. Please install those packages using your distro package
manager. This is a list of packages that you should have installed locally:

- Python 3.7
- Virtualenv or virtualenvwrapper
- Invoke (>= 1.0)
- Node.js and npm

Once everything is installed, and your virtualenv is activated, just run the
configure.sh script::

    $ sh configure.sh

This task creates a test database with a few conversations, comments and votes,
plus several users. Notably, it automatically creates the ``admin:admin <admin@admin.com>``
and ``user:user <user@user.com>``users.

Grab a cup of coffee while it downloads and install all dependencies. If
everything works, you should be able to run the server using the ``inv run``
command.


Running it
~~~~~~~~~~

Unless you prefer to type long Django management commands, use Invoke_ to start
the dev server::

    $ inv run

Before running, make sure you compiled all static assets. This command will
compile translations, build stylesheets and JavaScript

    $ inv i18n -c sass js

You can control many configurations using environment variables. To run using
the Brazilian Portuguese translation, for instance, just export the correct
COUNTRY setting:

    $ export COUNTRY=brasil

Tests are executed with Pytest_::

    $ pytest

Invoke manages many other important tasks, you can discover them using::

    $ inv -l

.. _Invoke: http://www.pyinvoke.org/
.. _Pytest: http://pytest.org


Semi-manual installation
~~~~~~~~~~~~~~~~~~~~~~~~

The script installs the invoke task runner, fetches all dependencies from pip,
and initializes the database. If you prefer (or if something goes wrong with the
previous instructions), you can do all steps manually. The first step is to
install the Invoke_ task runner to run each step of the installation (if you are
not familiar to Invoke, think of it a Python reinterpretation of Make. First
install invoke, then run the "configure" task::

    $ pip install invoke
    $ inv configure

It will ask a few questions and conduct the installation procedure.


Documentation
~~~~~~~~~~~~~

Documentation can be updated with `$ sphinx-build docs build/docs` and will be available at http://localhost:8000/docs.

Using docker
------------

If you want to use docker, build the containers and just start docker compose::

    $ sudo docker-compose -f docker/deploy/docker-compose.yml build
    $ sudo docker-compose -f docker/docker-compose.yml up -d

After the command, **ej-server** can be accessed at http://localhost:8000.

At some point, you probably will want to execute commands inside the container.
It is possible to open a bash shell in the main "web" container with::

    $ sudo docker-compose -f docker/docker-compose.yml run web bash


In fact, it integrates with invoke and we can replace "bash" by any sequence of
invoke tasks. For instance, we can migrate the database and run tests
afterwards by doing::

    $ sudo docker-compose -f docker/docker-compose.yml exec web db tests

If you have invoke installed on the host machine, you can use the short
version::

    $ inv docker-run dev


Tests
~~~~~

There are two ways to locally execute tests using docker-compose::

    $ sudo docker-compose -f docker/docker-compose.yml run web tests

or using inv::

    $ inv docker-run run -c tests     # uses postgresql
    $ inv docker-run single -c tests  # uses sqlite3
