+-----------------------+-----------------------+-----------------------+
| Environment           | CI Status             | Website               |
+=======================+=======================+=======================+
| Production            | |pipeline status|     | `ejplatform.org <http |
|                       |                       | s://ejplatform.org>`_ |
|                       |                       | _                     |
+-----------------------+-----------------------+-----------------------+
| Development           | |pipeline status|     | `dev.ejplatform.org < |
|                       |                       | http://dev.ejplatform |
|                       |                       | .org>`__              |
+-----------------------+-----------------------+-----------------------+


===========
EJ Platform
===========

Getting started
===============

Local development (virtualenv)
------------------------------


    ej-server REQUIRES Python 3.6. For ubuntu users:                    
    If you are using Ubuntu 14.04 or 16.04, you can use Felix Krull's    
    deadsnakes PPA at                                                    
    https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa:               
    sudo add-apt-repository ppa:deadsnakes/ppa                          
    sudo apt-get update                                                
    sudo apt-get install python3.6                                  

    Alternatively, you can use J Fernyhough's PPA at                 
    https://launchpad.net/~jonathonf/+archive/ubuntu/python-3.6:     
    sudo add-apt-repository ppa:jonathonf/python-3.6                 
    sudo apt-get update                                              
    sudo apt-get install python3.6                                   

    If you are using Ubuntu 16.10 or 17.04, then Python 3.6 is in the 
    universe repository, so you can just run:                         
    sudo apt-get update                                                    
    sudo apt-get install python3.6                                    


First install virtualenvwrapper in your machine (``sudo apt-get install virtualenvwrapper`` on
Debian based distributions). Clone this repo and create a virtual environment using
Python 3.6+::

    $ git clone http://github.com/ejplatform/ej-server/
    $ mkvirtualenv ej -p /usr/bin/python3.6
    (if the command don't run, reload bash or check your system path)

Now, go into the repository and run the configure script::

    $ cd ej-server
    $ ./configure.sh

Grab a cup of coffee while it downloads and install all dependencies. If
everything works, you should be able to run the server using the ``inv run``
command.

The script installs the invoke task runner, fetches all dependencies from pip,
and initializes the database. If you prefer, you can do all steps manually.
The first step is to install the Invoke_ task runner to run each step of the
installation (if you are not familiar to Invoke, think of it as Python's version
of Make)::

    $ pip install invoke

You can install dependencies manually using the files in /etc/requirements/, or
simply use the update-deps task. The later is preferable since it installs the
volatile dependencies in a special local/vendor/ folder::

    $ inv update-deps --all

Invoke allow us to execute a sequence of tasks very easily. The command bellow
will run migrations and populate the database with fake data for local
development::

    $ inv update-deps db db-assets db-fake

This creates a few conversations with comments and votes + several users and
a admin:admin <admin@admin.com> user. Use invoke to start the dev server::

    $ inv run


.. _Invoke: http://www.pyinvoke.org/

Tests are executed with Pytest_::

    $ pytest

.. _Pytest: http://pytest.org


Using docker
------------

If you want to use docker, just clone the repo and start docker compose::

    $ git clone http://github.com/ejplatform/ej-server/
    $ sudo docker-compose -f ./docker/develop/start.yml up -d

After the command, **ej-server** can be accessed at http://localhost:8000.


Tests
-----

There are two ways to locally execute the automated tests using
docker-compose:

-  If you already ran
   ``sudo docker-compose -f ./docker/local/start.yml up -d`` and the
   server is up and running, execute:

.. code:: bash

    sudo docker-compose -f ./docker/local/start.yml exec django pytest

-  If you just want to run the tests without necessarily getting up all
   the services available on local environment, the configuration file
   on docker-compose
   `docker/local/test.yml <https://github.com/ejplatform/ej-server/blob/master/docker/local/test.yml>`__
   will have only the necessary services to run the tests. To run the
   tests, execute:

.. code:: bash

    sudo docker-compose -f ./docker/local/test.yml run --rm django

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

Rocketchat Integration
----------------------

See the guidelines at
`docker/extensions <https://github.com/ejplatform/ej-server/blob/master/docker/extensions#using-rocketchat>`__.

.. |pipeline status| image:: https://gitlab.com/ejplatform/ej-server/badges/master/pipeline.svg
   :target: https://gitlab.com/ejplatform/ej-server/commits/master
.. |pipeline status| image:: https://gitlab.com/ejplatform/ej-server/badges/develop/pipeline.svg
   :target: https://gitlab.com/ejplatform/ej-server/commits/develop
.. |pipeline status| image:: https://gitlab.com/ejplatform/ej-server/badges/master/pipeline.svg
   :target: https://gitlab.com/ejplatform/ej-server/commits/master
.. |pipeline status| image:: https://gitlab.com/ejplatform/ej-server/badges/develop/pipeline.svg
   :target: https://gitlab.com/ejplatform/ej-server/commits/develop
