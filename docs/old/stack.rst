========
EJ Stack
========

Services
========

The most basic EJ stack consists of four containers running the following
services:

Nginx:
    The reverse proxy is the only container that needs to be publicly facing the
    network. It is based on a stock Nginx container that overrides nginx.conf
    and includes the static resources used by the platform.
Django:
    The container with the main Django application starts a Gunicorn application
    server and must connect with Nginx via either http (default) or sockets.
Postgres:
    The default database server. EJ will probably work with other databases
    supported by Django such as sqlite3 and MySQL, but this was not tested and
    it is not recommended.
Redis:
    The cache database. Used to store sessions, cache templates and other
    integrations with Django caching subsystem.


Optionally, we support integration with Rocketchat, which adds two more
containers:

Rocketchat:
    The vanilla container for the Rocketchat platform.
Mongo:
    Database used by Rocketchat.


Backend Technologies
====================

This section lists the main technologies used in the backend application.

Django_:
    The web server is based on the Django framework, version 2.0.
`Django REST Framework`_:
    EJ exposes a REST api at /api/v1/ powered by Django Rest Framework.
`Django Boogie`_:
    Django Boogie is a meta-framework that aims to complement Django and make
    developers more productive. It is used extensively in EJ and is maintained
    by one of its developers. Django Boogie cuts boilerplate in API and views
    creation and offers alternatives to some of Django's pain points such as
    settings management (which uses reusable classes in Boogie) and the query
    language (which has an API inspired on Pandas).
`Hyperpython`_:
    Another sister project, it implements an HTML DSL inside Python and is
    useful to organize HTML snippets to be consumed by templates or used to
    render whole HTML pages.
Numpy_ / Pandas_ / `Scikit-learn`_:
    The machine learning algorithms are powered mainly by a traditional Pyadata
    stack with Numpy, Pandas and Scikit-learn.

.. _Django: https://docs.djangoproject.com/en/2.1/
.. _Django REST Framework: http://www.django-rest-framework.org/
.. _Django Boogie: https://github.com/fabiommendes/django-boogie/
.. _Hyperpython: https://github.com/fabiommendes/hyperpython/
.. _Numpy: http://www.numpy.org/
.. _Pandas: https://pandas.pydata.org/
.. _Scikit-learn: http://scikit-learn.org/


Auxiliary Docker images
=======================

EJ uses some generic images pre-build with useful assets such as webdev tools,
Python etc. Those images

ejplatform/python:alpine:
    A derivative of debian:buster-slim with Python 3.6 and invoke.
ejplatform/docker-invoke:
    A derivative of the standard docker image with Python 3.6 and invoke.
ejplatform/builder:
    A derivative of debian:buster-slim with Python 3.6 and tools to build
    static assets such as Sass and Node.js
