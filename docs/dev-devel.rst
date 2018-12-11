#####################################
Preparing the Development Environment
#####################################

.. contents::
   :depth: 2


******************************
Local development (virtualenv)
******************************

EJ platform **requires** you to _`Prepare environment` + with the
development headers. Please install those packages using your distro package
manager. This is a list of packages that you should have installed locally:

- Python 3.6
- Virtualenv or virtualenvwrapper
- Invoke (>= 0.23)
- Sass
- Node.js

Once everything is installed, and your virtualenv is activated, just run the
configure.sh script::

    $ sh configure.sh

Grab a cup of coffee while it downloads and install all dependencies. If
everything works, you should be able to run the server using the ``inv run``
command.


Running it
==========

Unless you prefer to type long django management commands, use Invoke_ to start
the dev server::

    $ inv run

Before runing, make sure you regenerate the PO files and compile. It's necessary to compile sass either:

    $ inv i18n  
    
    $ inv i18n -c  
    
    $ inv sass run  

To run on brazilian portuguese:

    $ export COUNTRY=brasil

Tests are executed with Pytest_::

    $ pytest

Invoke manages many other important tasks, you can discover them using::

    $ inv -l

.. _Invoke: http://www.pyinvoke.org/
.. _Pytest: http://pytest.org


Semi-manual installation
========================

The script installs the invoke task runner, fetches all dependencies from pip,
and initializes the database. If you prefer (or if something goes wrong with the
previous instructions), you can do all steps manually. The first step is to
install the Invoke_ task runner to run each step of the installation (if you are
not familiar to Invoke, think of it a Python reinterpretation of Make::

    $ pip install invoke

You can install dependencies manually using the files in /etc/requirements/, or
simply use the update-deps task. The later is preferable since it installs the
volatile dependencies in a special folder that makes it easier and faster to
do further updates::

    $ inv update-deps --all

Invoke allow us to execute a sequence of tasks very easily. The command bellow
will run migrations and populate the database with fake data for local
development::

    $ inv update-deps db db-assets db-fake

This creates a few conversations with comments and votes plus several users and
an admin:admin <admin@admin.com> user.


************
Using docker
************

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
-----

There are two ways to locally execute tests using docker-compose::

    $ sudo docker-compose -f docker/docker-compose.yml run web tests

or using inv::

    $ inv docker-run run -c tests     # uses postgresql
    $ inv docker-run single -c tests  # uses sqlite3

