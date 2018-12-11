###########
Quick Start
###########

.. contents::
   :depth: 2

***************
Getting started
***************

First clone the repository and point to it::

    $ git clone http://github.com/ejplatform/ej-server/
    $ cd ej-server

If you use docker, you can quickly start the development server using the
command::

    $ sudo docker-compose -f docker/docker-compose.yml up

For most cases, however we recommend that you prepare your machine with some
tools. Developers may choose between docker or virtualenv for day to day
development. In both cases, we recommend that you have Invoke_ >= 0.23 installed
in your machine.

Docker will probably get you started quicker, but in the long run it may be
harder to integrate with your tools and often requires long builds not needed when
using virtualenv.

_Invoke: http://www.pyinvoke.org/

