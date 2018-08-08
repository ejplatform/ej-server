Prepare environment
===================

.. contents::
   :depth: 2

Ubuntu 14.04 to 16.04
---------------------

If you are using Ubuntu 14.04 to 16.04, you can use Felix Krull's deadsnakes
PPA at https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa::

    $ sudo add-apt-repository ppa:deadsnakes/ppa
    $ sudo apt-get update
    $ sudo apt-get install python3.6-dev virtualenvwrapper npm sass


Ubuntu 16.10+ and Debian 9+
---------------------------

For Ubuntu 16.10 and 17.04 do not come with Python 3.6 by default, but it is in
the Universe repository, You should be able to install it with the following commands::

    $ sudo apt-get update
    $ sudo apt-get install python3.6-dev npm sass


Fedora
------
If the python3 installed on your system is not 3.6, you can use the following
command to install it::

    $ sudo dnf install python36 npm ruby-sass


Arch Linux
----------
Arch Linux is fairly aggressive about keeping up with Python releases. It is
likely you already have the latest version. If not, you can use this command::

    $ sudo pacman -S python python-virtualenvwrapper npm ruby-sass


CentOS
------
The IUS Community does a nice job of providing newer versions of software for
“Enterprise Linux” distros (i.e. Red Hat Enterprise and CentOS). You can use
their work to help you install Python 3.

To install, you should first update your system with the yum package manager::

    $ sudo yum update
    $ sudo yum install yum-utils

You can then install the CentOS IUS package which will get you up to date with
their site::

    $ sudo yum install https://centos7.iuscommunity.org/ius-release.rpm

Finally you can then install Python and pip::

    $ sudo yum install python36u
    $ sudo yum install python36u-pip

For last, install node package manager and sass::

    $ curl --silent --location https://rpm.nodesource.com/setup_8.x | sudo bash -
    $ sudo yum install nodejs
    $ sudo npm install sass

Mac
---
We'll start by installing homebrew to make things easier and then Python 3, followed by Sass.

    $ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    $ brew install python
    $ brew install sass/sass/sass


Building from sources
---------------------

Step 1: Download the Source Code::

    $ wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tgz

Step 2: Prepare Your System::

1. The first step you should take when doing an operation like this is to update
the system packages on your machine before you start. On Debian, this is what
that looks like::

    $ sudo apt-get update
    $ sudo apt-get upgrade

2. Next, we want to make sure the system has the tools needed to build Python.
There are a bunch of them and you might already have some, but that’s fine. I’ve
listed them all in one command line, but you can break the list into shorter
commands by just repeating the sudo apt-get install -y portion:

- For apt-based systems (like Debian, Ubuntu, and Mint)::

    $ sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
        libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
        libncurses5-dev  libncursesw5-dev xz-utils tk-dev

- For yum-based systems (like CentOS)::

    $ sudo yum -y groupinstall development
    $ sudo yum -y install zlib-devel

Step 3: Build Python

1. Once you have the prerequisites and the tar file, you can unpack the source
into a directory. Note that the following command will create a new directory
called Python-3.6.5 under the one you are in::

    $ tar xvf Python-3.6.5.tgz
    $ cd Python-3.6.5

2. Now you need to run the ./configure tool to prepare the build::

    $ ./configure --enable-optimizations --with-ensurepip=install

3. Next, you build the Python programs using make. The -j option simply tells
make to split the building into parallel steps to speed up the compilation. Even
with the parallel builds, this step can take a several minutes::

    $ make -j 8

4. Then, you’ll want to install your new version of Python. You’ll use the
altinstall target here in order to not overwrite the system’s version of Python.
Since you’re installing Python into /usr/bin, you’ll need to run as root::

    $ sudo make altinstall

Step 4: Setup Sass

1. For last, install node package manager and sass::

    $ sudo apt-get install npm
    $ sudo npm install sass
