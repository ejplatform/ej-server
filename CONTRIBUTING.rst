Add features to ej-server
======================================

For each issue to be solved, follow the procedure below:

-  In case of your development environment isn't already built, then clone the repository, follow the installation guide at `README.rst`_ and install the hooks to check your static code with::

    $ inv install-hooks

-  Checkout to branch ``dev`` or any other branch you may want to create to solve your issue. E.g.::

   $ git checkout dev

-  Always run the tests before a commit you do otherwise your pull request
will not be merged! E.g.::

   $ inv test

-  At the end of your issue, open a pull request to branch MASTER::

   ejplatform/ej-server/master <- ejplatform/ej-server/dev

-  Wait until Travis CI, GitLab CI and Code Climate runs all the integration tests.
-  If all the tests passed any contributor can merge your PR.  :rocket:
-  If you create a branch different from ``dev``, than always delete it after your PR be merged.

.. _README.rst: README.rst
