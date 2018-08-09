.. image:: https://api.codeclimate.com/v1/badges/fd8f8c7d5d2bc74c38df/maintainability
   :target: https://codeclimate.com/github/ejplatform/ej-server/maintainability
   :alt: Maintainability
.. image:: https://gitlab.com/ejplatform/ej-server/badges/master/pipeline.svg
   :target: https://gitlab.com/ejplatform/ej-server/commits/master
.. image:: https://gitlab.com/ejplatform/ej-server/badges/develop/pipeline.svg
   :target: https://gitlab.com/ejplatform/ej-server/commits/develop


===========
EJ Platform
===========

Getting started
===============

Local development (virtualenv)
------------------------------

EJ platform **requires** Python 3.6 + the development headers. Please install
those packages using your distro package manager.

Install Python 3.6.5
====================

Ubuntu 14.04 to 16.04
---------------------

If you are using Ubuntu 14.04 to 16.04, you can use Felix Krull's deadsnakes PPA at https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa::

    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install python3.6-dev
    sudo apt-get install npm
    sudo npm install sass

Ubuntu 16.10 and 17.04
----------------------
For Ubuntu 16.10 and 17.04 do not come with Python 3.6 by default, but it is in the Universe repository, You should be able to install it with the following commands::

    sudo apt-get update
    sudo apt-get install python3.6-dev
    sudo apt-get install npm
    sudo npm install sass

Linux Mint
----------
Mint and Ubuntu use the same package management system, which frequently makes life easier. You can follow the instructions above for Ubuntu 14.04. The “deadsnakes” PPA works with Mint.

Debian
------
We found sources that indicated that the Ubuntu 16.10 method would work for Debian, but we never found a path to get it to work on Debian 9. Instead, we ended up making Python from source as listed below.

Debian 9
--------

Step 1: Download the Source Code::

$ wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tgz

Step 2: Prepare Your System::

1. The first step you should take when doing an operation like this is to update the system packages on your machine before you start. On Debian, this is what that looks like::

    $ sudo apt-get update
    $ sudo apt-get upgrade

2. Next, we want to make sure the system has the tools needed to build Python. There are a bunch of them and you might already have some, but that’s fine. I’ve listed them all in one command line, but you can break the list into shorter commands by just repeating the sudo apt-get install -y portion:


- For apt-based systems (like Debian, Ubuntu, and Mint)::

    $ sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev  libncursesw5-dev xz-utils tk-dev

- For yum-based systems (like CentOS)::

    $ sudo yum -y groupinstall development
    $ sudo yum -y install zlib-devel

Step 3: Build Python

1. Once you have the prerequisites and the tar file, you can unpack the source into a directory. Note that the following command will create a new directory called Python-3.6.5 under the one you are in::

    $ tar xvf Python-3.6.5.tgz
    $ cd Python-3.6.5

2. Now you need to run the ./configure tool to prepare the build::

    $ ./configure --enable-optimizations --with-ensurepip=install

3. Next, you build the Python programs using make. The -j option simply tells make to split the building into parallel steps to speed up the compilation. Even with the parallel builds, this step can take a several minutes::

    $ make -j 8

4. Then, you’ll want to install your new version of Python. You’ll use the altinstall target here in order to not overwrite the system’s version of Python. Since you’re installing Python into /usr/bin, you’ll need to run as root::

    $ sudo make altinstall

Step 4: Setup Sass

1. For last, install node package manager and sass::

    $ sudo apt-get install npm
    $ sudo npm install sass


CentOS
------
The IUS Community does a nice job of providing newer versions of software for “Enterprise Linux” distros (i.e. Red Hat Enterprise and CentOS). You can use their work to help you install Python 3.

To install, you should first update your system with the yum package manager::

    $ sudo yum update
    $ sudo yum install yum-utils

You can then install the CentOS IUS package which will get you up to date with their site::

    $ sudo yum install https://centos7.iuscommunity.org/ius-release.rpm

Finally you can then install Python and Pip::

    $ sudo yum install python36u
    $ sudo yum install python36u-pip

For last, install node package manager and sass::

    $ curl --silent --location https://rpm.nodesource.com/setup_8.x | sudo bash -
    $ sudo yum install nodejs
    $ sudo npm install sass

Fedora
------
If the python3 installed on your version is not 3.6, you can use the following command to install it::

    $ sudo dnf install python36

Then install node package manager::

    $ sudo dnf install nodejs
    $ sudo dnf install npm
    $ sudo npm install sass

Arch Linux
----------
Arch Linux is fairly aggressive about keeping up with Python releases. It is likely you already have the latest version. If not, you can use this command::

    $ packman -S python
    $ packman -S nodejs
    $ npm install sass

Verify Your Python Install
--------------------------

Finally, you can test out your new Python version::

    $ python3.6 -V

Manual Installation Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First install virtualenvwrapper in your machine (``sudo apt-get install virtualenvwrapper`` on Debian based distributions).
Clone this repo and create a virtual environment using Python 3.6.5::

    $ git clone http://github.com/ejplatform/ej-server/
    $ mkvirtualenv ej -p /usr/bin/python3.6
    (if the command don't run, reload bash or check your system path)

Now, go into the repository and run the configure script::

    $ cd ej-server
    $ ./configure.sh

Grab a cup of coffee while it downloads and install all dependencies. If
everything works, you should be able to run the server using the ``inv run``
command.


(Semi-)manual installation
~~~~~~~~~~~~~~~~~~~~~~~~~~

The script installs the invoke task runner, fetches all dependencies from pip,
and initializes the database. If you prefer (or if something goes wrong with the
previous instructions), you can do all steps manually. The first step is to
install the Invoke_ task runner to run each step of the installation (if you are
not familiar to Invoke, think of it as Python's version
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
a admin:admin <admin@admin.com> user.

Running it
~~~~~~~~~~

Unless you prefer to type long django management commands, use invoke to start
the dev server::

    $ inv run


.. _Invoke: http://www.pyinvoke.org/

Tests are executed with Pytest_::

    $ pytest

.. _Pytest: http://pytest.org


Using docker
------------

If you want to use docker, just clone the repo and start docker compose::

    $ git clone http://github.com/ejplatform/ej-server/
    $ sudo docker-compose -f ./docker/docker-compose.yml build
    $ sudo docker-compose -f ./docker/docker-compose.yml up

After the command, **ej-server** can be accessed at http://localhost:8000.

You can open a terminal to run management commands like creating migrations,
updating the database, etc using::

$ sudo docker-compose -f ./docker/docker-compose.yml run web bash

If you want to run docker, but develop without running the django server,
use the idle version and execute the conteiner bash manually::

    $ sudo docker-compose -f ./docker/production/django/build.yml build
    $ sudo docker-compose -f ./docker/develop/idle.yml up -d
    $ sudo docker-compose -f ./docker/develop/idle.yml exec django bash

Now, you can execute django commands, inv tasks and pytest normally.

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

