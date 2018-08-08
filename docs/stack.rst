EJ Stack
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
    The default database server. EJ should probably work with other databases
    supported by Django such as sqlite3 and MySQL, but this is not recommended.
Redis:
    The cache server. Used to store sessions, cache templates and other
    integrations with Django caching subsystem.
