=====================
Preparing environment
=====================

Python
======

EJ requires Python 3.7+ and a POSIX environment. If you use a recent version of
a Linux distribution, it is probably already installed in your system, otherwise
you will have to follow system-specific instructions:

* `Ubuntu <https://websiteforstudents.com/installing-the-latest-python-3-7-on-ubuntu-16-04-18-04/>`

If you have a fairly recent distribution, try one of the instructions bellow:


Ubuntu/Debian
-------------

Everything you need is one apt away::

    $ sudo apt update
    $ sudo apt install python3-dev npm
    $ sudo pip install invoke~=1.0


Archlinux
---------

Everything you need is package for Pacman::

    $ sudo pacman -S python npm
    $ sudo pip install invoke~=1.0
