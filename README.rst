.. image:: https://api.codeclimate.com/v1/badges/fd8f8c7d5d2bc74c38df/maintainability
   :target: https://codeclimate.com/github/ejplatform/ej-server/maintainability
   :alt: Maintainability
.. image:: https://codecov.io/gh/ejplatform/ej-server/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/ejplatform/ej-server
.. image:: https://gitlab.com/ejplatform/ej-server/badges/master/pipeline.svg
    :target: https://gitlab.com/ejplatform/ej-server/commits/master



=============================
EJ Platform  :speech_balloon:
=============================

Would you like to visit the EJ website?

Acess Here: :arrow_right: http://ejplatform.org.



Getting started :runner:
=============================

First clone the repository::

    $ git clone http://github.com/ejplatform/ej-server/
    $ cd ej-server


Using Docker to start development server :computer:
---------------------------------------------------

Run the Commands::

    $ pip3 install invoke --user
    $ inv docker-build
    $ inv docker up

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


Using Virtualenv to start Local development :computer:
---------------------------------------------------

For most cases, however, we recommend that you prepare your machine with some
extra tools. Developers may choose between Docker or Poetry/Virtualenv for day to day
development. In both cases, we recommend that you have Invoke_ installed
in your machine to make execution of chores easier.

This is a list of packages that you should have installed locally before we
start:

- Python 3.6+ (Python 3.7 is recommended)
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

    $ bash
    $ mkvirtualenv ej -p /usr/bin/python3

This command creates and activates the virtualenv. When you want to work with the
repository in a later time, activate the virtual env using the command::

    workon ej

The following steps are handled by the configure.sh script::

    $ sh configure.sh

Or if you have problems, try::

    $ bash configure.sh

This task creates a test database with a few conversations, users, comments, and
votes. Notably, it automatically creates an admin user 
(password:admin, email: admin@admin.com) a regular user (password: user, email: user@user.com).

This step takes some time. Grab a cup of :coffee: while it downloads and install
all dependencies. 


Running the project :trophy:
=============================

First compile the part of the code responsible for the CSS of the application

    $ inv sass

Unless you prefer to type long Django management commands, use Invoke_ to start
the dev server::


    $ inv run

After the command, **ej-server** can be accessed at http://localhost:8000.



Configuration commands :wrench:
=============================


You can control many configurations using environment variables. To run using
the Brazilian Portuguese translation, for instance, just export the correct
COUNTRY setting:

    $ export COUNTRY=brasil

Depending on your network configurations, you might need to set the ALLOWED_HOSTS
setting for your Django installation. This is a basic security setting that
controls which hosts can serve pages securely. In non-production settings, set
DJANGO_ALLOWED_HOSTS environment variable to * to allow connections in any
network topology.

    $ DJANGO_ALLOWED_HOSTS=*

Invoke manages many other important tasks, you can discover them using::

    $ inv -l

If you are making changes to EJ codebase, do not forget to run tests frequently.
EJ uses Pytest_::

    $ pytest

.. _Invoke: http://www.pyinvoke.org/

.. _Pytest: http://pytest.org


Documentation the project :file_folder:
=============================

Documentation can be updated with `$ inv docs` and will be available at the
`build/docs/` directory.


Changing theme the project :art:
=============================

The previous commands build EJ using the "default" theme. EJ accepts additional
themes and currently comes pre-installed with the alternate "cpa" theme. The
first step is to rebuild static assets::

    $ inv sass -t cpa js db-assets

Now run the server using the --theme flag::

    $ inv run -t cpa


Contributing :file_folder:
=============================

Please make sure to read the guide before making a pull request. After you've read, don't forget to take an issue!

`Guide <https://github.com/gces-empjuntos/ej-server/blob/develop/CONTRIBUTING.rst>`_

`Issues Templates for contributing <https://github.com/gces-empjuntos/ej-server/tree/change_README.md/ISSUE_TEMPLATES>`_


Tests :heavy_check_mark:
=============================

Running Tests with Docker
-------------------------

    use the following command::

        $ sudo docker-compose -f docker/docker-compose.yml run web tests


Running Tests with Inv
-------------------------

    use the following command::

        $ inv docker-run run -c tests     # uses postgresql
        $ inv docker-run single -c tests  # uses sqlite3

